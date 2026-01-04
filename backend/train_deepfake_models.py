"""
Fine-tune existing deepfake detection models on custom dataset.
This script improves the models' ability to detect specific types of AI-generated images.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoImageProcessor, AutoModelForImageClassification
from transformers import Trainer, TrainingArguments
from PIL import Image
import os
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# Paths
DATA_PATH = Path("../test_data")
CACHE_DIR = "./models_cache/huggingface"
OUTPUT_DIR = "./fine_tuned_models"

# Configuration
BATCH_SIZE = 16  # Reduce if you run out of memory
EPOCHS = 5
LEARNING_RATE = 2e-5
IMAGE_SIZE = 224


class DeepfakeDataset(Dataset):
    """Dataset for deepfake detection with memory-efficient loading"""
    
    def __init__(self, image_paths, labels, processor, augment=False):
        self.image_paths = image_paths
        self.labels = labels
        self.processor = processor
        self.augment = augment
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Load image
        img_path = self.image_paths[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            
            # Remove batch dimension and convert to dict
            pixel_values = inputs['pixel_values'].squeeze(0)
            
            return {
                'pixel_values': pixel_values,
                'labels': torch.tensor(self.labels[idx], dtype=torch.long)
            }
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return a dummy sample
            dummy_image = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), color='black')
            inputs = self.processor(images=dummy_image, return_tensors="pt")
            return {
                'pixel_values': inputs['pixel_values'].squeeze(0),
                'labels': torch.tensor(0, dtype=torch.long)
            }


def load_dataset_paths(data_path):
    """
    Load image paths and labels from the test_data directory.
    Returns paths and labels (0=real, 1=fake)
    """
    print("\n" + "="*60)
    print("Loading dataset...")
    print("="*60)
    
    image_paths = []
    labels = []
    
    # Map folders to labels
    folder_mapping = {
        'real': 0,           # Real images
        'dalle': 1,          # AI-generated (fake)
        'gan_faces': 1,      # AI-generated (fake)
        'midjourney': 1,     # AI-generated (fake)
        'stable_diffusion': 1  # AI-generated (fake)
    }
    
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    
    for folder_name, label in folder_mapping.items():
        folder_path = data_path / folder_name
        
        if not folder_path.exists():
            print(f"⚠ Warning: Folder '{folder_name}' not found, skipping...")
            continue
        
        # Get all image files
        images = [
            f for f in folder_path.iterdir() 
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        print(f"✓ Found {len(images):,} images in '{folder_name}' (label={label})")
        
        for img_path in images:
            image_paths.append(str(img_path))
            labels.append(label)
    
    print(f"\nTotal images: {len(image_paths):,}")
    print(f"Real images: {labels.count(0):,}")
    print(f"Fake images: {labels.count(1):,}")
    
    return image_paths, labels


def prepare_datasets(image_paths, labels, processor, test_size=0.2, val_size=0.1):
    """Split data into train/val/test sets"""
    print("\n" + "="*60)
    print("Splitting dataset...")
    print("="*60)
    
    # First split: train+val vs test
    train_val_paths, test_paths, train_val_labels, test_labels = train_test_split(
        image_paths, labels, test_size=test_size, random_state=42, stratify=labels
    )
    
    # Second split: train vs val
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        train_val_paths, train_val_labels, test_size=val_size/(1-test_size), 
        random_state=42, stratify=train_val_labels
    )
    
    print(f"Training set: {len(train_paths):,} images")
    print(f"Validation set: {len(val_paths):,} images")
    print(f"Test set: {len(test_paths):,} images")
    
    # Create datasets
    train_dataset = DeepfakeDataset(train_paths, train_labels, processor, augment=True)
    val_dataset = DeepfakeDataset(val_paths, val_labels, processor, augment=False)
    test_dataset = DeepfakeDataset(test_paths, test_labels, processor, augment=False)
    
    return train_dataset, val_dataset, test_dataset


def compute_metrics(eval_pred):
    """Compute accuracy and other metrics"""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    accuracy = (predictions == labels).mean()
    
    # Calculate precision, recall for fake class
    true_positives = ((predictions == 1) & (labels == 1)).sum()
    false_positives = ((predictions == 1) & (labels == 0)).sum()
    false_negatives = ((predictions == 0) & (labels == 1)).sum()
    
    precision = true_positives / (true_positives + false_positives + 1e-10)
    recall = true_positives / (true_positives + false_negatives + 1e-10)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-10)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


def train_model(model_name, model, processor, train_dataset, val_dataset, output_dir):
    """Fine-tune a model using HuggingFace Trainer"""
    print("\n" + "="*60)
    print(f"Training: {model_name}")
    print("="*60)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f'{output_dir}/logs',
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        dataloader_num_workers=0,  # Set to 0 to avoid multiprocessing issues on Windows
        remove_unused_columns=False,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Train
    print(f"\nStarting training for {EPOCHS} epochs...")
    train_result = trainer.train()
    
    # Save the model
    print(f"\nSaving fine-tuned model to {output_dir}")
    trainer.save_model(output_dir)
    processor.save_pretrained(output_dir)
    
    # Evaluate
    print("\nEvaluating on validation set...")
    eval_results = trainer.evaluate()
    
    print("\n" + "="*60)
    print("Training Results:")
    print("="*60)
    for key, value in eval_results.items():
        print(f"{key}: {value:.4f}")
    
    return trainer, eval_results


def test_model(trainer, test_dataset):
    """Test the fine-tuned model"""
    print("\n" + "="*60)
    print("Testing on held-out test set...")
    print("="*60)
    
    test_results = trainer.evaluate(test_dataset)
    
    print("\nTest Results:")
    print("="*60)
    for key, value in test_results.items():
        print(f"{key}: {value:.4f}")
    
    return test_results


def main():
    print("\n" + "="*60)
    print("DEEPFAKE DETECTION MODEL FINE-TUNING")
    print("="*60)
    
    # Check if data directory exists
    if not DATA_PATH.exists():
        print(f"\n❌ Error: Data directory not found at {DATA_PATH}")
        print("Please ensure your test_data folder is in the parent directory.")
        return
    
    # Load dataset
    image_paths, labels = load_dataset_paths(DATA_PATH)
    
    if len(image_paths) == 0:
        print("\n❌ Error: No images found in dataset!")
        return
    
    # Model 1: Primary model
    print("\n" + "="*60)
    print("TRAINING MODEL 1: prithivMLmods/Deep-Fake-Detector-Model")
    print("="*60)
    
    try:
        processor1 = AutoImageProcessor.from_pretrained(
            "prithivMLmods/Deep-Fake-Detector-Model",
            cache_dir=CACHE_DIR
        )
        model1 = AutoModelForImageClassification.from_pretrained(
            "prithivMLmods/Deep-Fake-Detector-Model",
            cache_dir=CACHE_DIR,
            num_labels=2,  # Binary classification
            ignore_mismatched_sizes=True
        ).to(DEVICE)
        
        # Prepare datasets
        train_ds1, val_ds1, test_ds1 = prepare_datasets(
            image_paths, labels, processor1
        )
        
        # Train
        output_dir1 = f"{OUTPUT_DIR}/prithiv_finetuned"
        trainer1, results1 = train_model(
            "Primary Model", model1, processor1, train_ds1, val_ds1, output_dir1
        )
        
        # Test
        test_results1 = test_model(trainer1, test_ds1)
        
    except Exception as e:
        print(f"\n❌ Error training Model 1: {e}")
        import traceback
        traceback.print_exc()
    
    # Model 2: Alternative model
    print("\n" + "="*60)
    print("TRAINING MODEL 2: dima806/deepfake_vs_real_image_detection")
    print("="*60)
    
    try:
        processor2 = AutoImageProcessor.from_pretrained(
            "dima806/deepfake_vs_real_image_detection",
            cache_dir=CACHE_DIR
        )
        model2 = AutoModelForImageClassification.from_pretrained(
            "dima806/deepfake_vs_real_image_detection",
            cache_dir=CACHE_DIR,
            num_labels=2,
            ignore_mismatched_sizes=True
        ).to(DEVICE)
        
        # Prepare datasets
        train_ds2, val_ds2, test_ds2 = prepare_datasets(
            image_paths, labels, processor2
        )
        
        # Train
        output_dir2 = f"{OUTPUT_DIR}/dima_finetuned"
        trainer2, results2 = train_model(
            "Alternative Model", model2, processor2, train_ds2, val_ds2, output_dir2
        )
        
        # Test
        test_results2 = test_model(trainer2, test_ds2)
        
    except Exception as e:
        print(f"\n❌ Error training Model 2: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETE!")
    print("="*60)
    print(f"\nFine-tuned models saved in: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Update ensemble_detector.py to load from fine_tuned_models directory")
    print("2. Test the improved models on new images")


if __name__ == "__main__":
    main()

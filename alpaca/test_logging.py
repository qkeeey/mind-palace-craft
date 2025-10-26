"""
Test script to verify logging is working correctly
"""

import os
import sys
from logging_config import setup_logger, ProgressLogger
from pathlib import Path

def test_basic_logging():
    """Test basic logging functionality"""
    print("\n" + "="*60)
    print("Testing Basic Logging")
    print("="*60)
    
    logger = setup_logger("test_basic", "test_basic.log")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("\n✅ Basic logging test complete")
    print(f"Check logs directory for: test_basic.log")

def test_progress_logging():
    """Test progress logging"""
    print("\n" + "="*60)
    print("Testing Progress Logging")
    print("="*60)
    
    logger = setup_logger("test_progress", "test_progress.log")
    
    progress = ProgressLogger(logger, 10, "Testing items")
    
    for i in range(10):
        progress.update(message=f"Processing item {i+1}")
    
    progress.complete("All items processed successfully")
    
    print("\n✅ Progress logging test complete")
    print(f"Check logs directory for: test_progress.log")

def test_exception_logging():
    """Test exception logging"""
    print("\n" + "="*60)
    print("Testing Exception Logging")
    print("="*60)
    
    logger = setup_logger("test_exception", "test_exception.log")
    
    try:
        # Intentionally cause an error
        result = 1 / 0
    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print("Exception logged with full traceback")
    
    print("\n✅ Exception logging test complete")
    print(f"Check logs directory for: test_exception.log")

def test_all_services():
    """Test logging for all services"""
    print("\n" + "="*60)
    print("Testing All Service Logging")
    print("="*60)
    
    # Test imports
    try:
        from pdf_extract import extract_text_with_groq
        print("✅ PDF Extract imports successfully")
    except Exception as e:
        print(f"❌ PDF Extract import failed: {e}")
    
    try:
        from concept_generator import ConceptGenerator
        print("✅ Concept Generator imports successfully")
    except Exception as e:
        print(f"❌ Concept Generator import failed: {e}")
    
    try:
        from association_generator import AssociationGenerator
        print("✅ Association Generator imports successfully")
    except Exception as e:
        print(f"❌ Association Generator import failed: {e}")
    
    try:
        from api_server import app
        print("✅ API Server imports successfully")
    except Exception as e:
        print(f"❌ API Server import failed: {e}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LOGGING SYSTEM TEST")
    print("="*60)
    
    # Get logs directory
    logs_dir = Path(__file__).parent / "logs"
    print(f"\nLogs will be saved to: {logs_dir.absolute()}")
    
    if not logs_dir.exists():
        print("Creating logs directory...")
        logs_dir.mkdir(exist_ok=True)
    
    # Run tests
    test_basic_logging()
    test_progress_logging()
    test_exception_logging()
    test_all_services()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)
    print(f"\nCheck the logs directory for detailed logs:")
    print(f"  {logs_dir.absolute()}")
    print("\nLog files created:")
    for log_file in sorted(logs_dir.glob("*.log")):
        size = log_file.stat().st_size
        print(f"  - {log_file.name} ({size} bytes)")

if __name__ == "__main__":
    main()

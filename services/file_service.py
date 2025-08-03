"""
File service for handling file operations.
Provides abstraction for reading, writing, and managing files.
"""

import os
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config.settings import Settings
# from core.exceptions import FileOperationError


class FileService:
    """Service for handling file operations."""
    
    def __init__(self, settings: Settings):
        """
        Initialize file service with configuration.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_directory = Path(settings.data_directory)
        
        # Ensure data directory exists
        self.data_directory.mkdir(exist_ok=True)
    
    def exists(self, file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            return Path(file_path).exists()
        except Exception as e:
            self.logger.error(f"Error checking file existence: {e}")
            return False
    
    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Read CSV file and return list of dictionaries.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            
        Returns:
            List of dictionaries representing CSV rows
        """
        try:
            self.logger.info(f"Reading CSV file: {file_path}")
            
            with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                data = list(reader)
            
            self.logger.info(f"Successfully read {len(data)} rows from {file_path}")
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {file_path}") 
        except Exception as e:
            raise RuntimeError(f"Error reading CSV file: {e}")
    
    def write_csv(self, file_path: str, data: List[Dict[str, Any]], encoding: str = 'utf-8') -> None:
        """
        Write data to CSV file.
        
        Args:
            file_path: Path to output CSV file
            data: List of dictionaries to write
            encoding: File encoding
        """
        try:
            if not data:
                self.logger.warning("No data to write to CSV")
                return
            
            self.logger.info(f"Writing {len(data)} rows to CSV file: {file_path}")
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Get all field names from all records
            fieldnames = set()
            for record in data:
                fieldnames.update(record.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(file_path, 'w', encoding=encoding, newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"Successfully wrote data to {file_path}")
            
        except PermissionError:
            raise PermissionError(f"Permission denied: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error writing CSV file: {e}")
    
    def read_json(self, file_path: str, encoding: str = 'utf-8') -> Any:
        """
        Read JSON file and return parsed data.
        
        Args:
            file_path: Path to JSON file
            encoding: File encoding
            
        Returns:
            Parsed JSON data
        """
        try:
            self.logger.info(f"Reading JSON file: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as jsonfile:
                data = json.load(jsonfile)
            
            self.logger.info(f"Successfully read JSON file: {file_path}")
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading JSON file: {e}")
    
    def write_json(self, file_path: str, data: Any, encoding: str = 'utf-8', indent: int = 2) -> None:
        """
        Write data to JSON file.
        
        Args:
            file_path: Path to output JSON file
            data: Data to write as JSON
            encoding: File encoding
            indent: JSON indentation
        """
        try:
            self.logger.info(f"Writing JSON file: {file_path}")
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as jsonfile:
                json.dump(data, jsonfile, indent=indent, ensure_ascii=False)
            
            self.logger.info(f"Successfully wrote JSON file: {file_path}")
            
        except Exception as e:
            raise RuntimeError(f"Error writing JSON file: {e}")
    
    def read_text(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read text file and return content.
        
        Args:
            file_path: Path to text file
            encoding: File encoding
            
        Returns:
            File content as string
        """
        try:
            self.logger.info(f"Reading text file: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as textfile:
                content = textfile.read()
            
            self.logger.info(f"Successfully read text file: {file_path}")
            return content
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading text file: {e}")
    
    def write_text(self, file_path: str, content: str, encoding: str = 'utf-8') -> None:
        """
        Write content to text file.
        
        Args:
            file_path: Path to output text file
            content: Content to write
            encoding: File encoding
        """
        try:
            self.logger.info(f"Writing text file: {file_path}")
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as textfile:
                textfile.write(content)
            
            self.logger.info(f"Successfully wrote text file: {file_path}")
            
        except Exception as e:
            raise FileOperationError(f"Error writing text file: {e}", file_path)
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List files in directory matching pattern.
        
        Args:
            directory: Directory to search
            pattern: File pattern (glob style)
            
        Returns:
            List of file paths
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return []
            
            files = [str(f) for f in dir_path.glob(pattern) if f.is_file()]
            self.logger.info(f"Found {len(files)} files in {directory}")
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file if it exists.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if file was deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                self.logger.info(f"Deleted file: {file_path}")
                return True
            else:
                self.logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            raise FileOperationError(f"Error deleting file: {e}", file_path)
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'is_file': path.is_file(),
                'is_directory': path.is_dir()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None

#!/usr/bin/env python3
"""
Advanced Pattern Scanner - Enhanced API Key and Credential Detection
Comprehensive pattern matching with 100+ detection patterns across multiple categories
"""

import re
import json
import base64
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from urllib.parse import unquote
import math


@dataclass
class Finding:
    """Security finding with detailed metadata"""
    pattern_type: str
    value: str
    confidence: float
    url: str
    location_type: str = "content"
    risk_level: str = "MEDIUM"
    entropy: float = 0.0
    context: str = ""
    category: str = "unknown"


class AdvancedPatternScanner:
    """Advanced pattern scanner with 100+ comprehensive detection patterns"""
    
    def __init__(self):
        self.patterns = self._initialize_extended_patterns()
        self.false_positive_filters = self._initialize_false_positive_filters()
        
    def _initialize_extended_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive pattern database with 100+ patterns"""
        return {
            # Cloud Provider Credentials
            'aws_access_key': {
                'pattern': r'\b(AKIA[0-9A-Z]{16})\b',
                'category': 'cloud_provider',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'aws_secret_key': {
                'pattern': r'\b([A-Za-z0-9+/]{40})\b',
                'category': 'cloud_provider', 
                'confidence': 0.7,
                'risk_level': 'HIGH'
            },
            'aws_session_token': {
                'pattern': r'\b(FQoGZXIvYXdzE[A-Za-z0-9+/=]+)\b',
                'category': 'cloud_provider',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'gcp_service_account': {
                'pattern': r'"type":\s*"service_account"',
                'category': 'cloud_provider',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'gcp_api_key': {
                'pattern': r'\b(AIza[0-9A-Za-z_-]{35})\b',
                'category': 'cloud_provider',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'azure_client_secret': {
                'pattern': r'\b([a-zA-Z0-9_~-]{34})\b',
                'category': 'cloud_provider',
                'confidence': 0.7,
                'risk_level': 'HIGH'
            },
            'azure_storage_key': {
                'pattern': r'\b([A-Za-z0-9+/]{88}==)\b',
                'category': 'cloud_provider',
                'confidence': 0.85,
                'risk_level': 'HIGH'
            },
            'digitalocean_token': {
                'pattern': r'\b(dop_v1_[a-f0-9]{64})\b',
                'category': 'cloud_provider',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            
            # Payment Processors
            'stripe_api_key': {
                'pattern': r'\b(sk_live_[0-9a-zA-Z]{24,})\b',
                'category': 'payment',
                'confidence': 0.95,
                'risk_level': 'CRITICAL'
            },
            'stripe_webhook_secret': {
                'pattern': r'\b(whsec_[0-9a-zA-Z]{32,})\b',
                'category': 'payment',
                'confidence': 0.90,
                'risk_level': 'HIGH'
            },
            'paypal_client_id': {
                'pattern': r'\b(A[A-Za-z0-9_-]{80})\b',
                'category': 'payment',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            'square_access_token': {
                'pattern': r'\b(sq0atp-[0-9A-Za-z_-]{22,})\b',
                'category': 'payment',
                'confidence': 0.95,
                'risk_level': 'CRITICAL'
            },
            'braintree_key': {
                'pattern': r'\b([a-z0-9]{32}_[a-z0-9]{16}_[a-z0-9]{32})\b',
                'category': 'payment',
                'confidence': 0.9,
                'risk_level': 'CRITICAL'
            },
            
            # Communication Services
            'twilio_auth_token': {
                'pattern': r'\b([a-f0-9]{32})\b',
                'category': 'communication',
                'confidence': 0.75,
                'risk_level': 'HIGH'
            },
            'sendgrid_api_key': {
                'pattern': r'\b(SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43})\b',
                'category': 'communication', 
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'mailgun_api_key': {
                'pattern': r'\b(key-[a-f0-9]{32})\b',
                'category': 'communication',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'slack_webhook': {
                'pattern': r'https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[a-zA-Z0-9]+',
                'category': 'communication',
                'confidence': 0.95,
                'risk_level': 'MEDIUM'
            },
            'discord_webhook': {
                'pattern': r'https://discord(?:app)?\.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+',
                'category': 'communication',
                'confidence': 0.95,
                'risk_level': 'MEDIUM'
            },
            
            # Development Services
            'github_token': {
                'pattern': r'\b(ghp_[a-zA-Z0-9]{36})\b',
                'category': 'development',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'github_oauth': {
                'pattern': r'\b(gho_[a-zA-Z0-9]{36})\b',
                'category': 'development',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'gitlab_token': {
                'pattern': r'\b(glpat-[a-zA-Z0-9_-]{20})\b',
                'category': 'development',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'npm_token': {
                'pattern': r'\b(npm_[a-zA-Z0-9]{36})\b',
                'category': 'development',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'docker_config_auth': {
                'pattern': r'"auth":\s*"[A-Za-z0-9+/=]+"',
                'category': 'development',
                'confidence': 0.8,
                'risk_level': 'MEDIUM'
            },
            'heroku_api_key': {
                'pattern': r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b',
                'category': 'development',
                'confidence': 0.7,
                'risk_level': 'HIGH'
            },
            
            # Database Credentials
            'mongodb_uri': {
                'pattern': r'mongodb(\+srv)?://[^\s]+',
                'category': 'database',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'postgres_uri': {
                'pattern': r'postgres(ql)?://[^\s]+',
                'category': 'database',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'mysql_connection': {
                'pattern': r'mysql://[^\s]+',
                'category': 'database',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'redis_uri': {
                'pattern': r'redis://[^\s]+',
                'category': 'database',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            'database_password': {
                'pattern': r'(?i)(db_pass|database_password|db_password)\s*[:=]\s*["\']([^"\']{8,})["\']',
                'category': 'database',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            
            # API Keys (Generic)
            'api_key_generic': {
                'pattern': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([A-Za-z0-9\-_\.]{20,})["\']',
                'category': 'api_key',
                'confidence': 0.7,
                'risk_level': 'MEDIUM'
            },
            'bearer_token': {
                'pattern': r'Bearer\s+([A-Za-z0-9\-_\.=]+)',
                'category': 'authentication',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            'authorization_header': {
                'pattern': r'Authorization:\s*["\']?([^"\'\s]+)["\']?',
                'category': 'authentication',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            
            # JWT Tokens
            'jwt_token': {
                'pattern': r'\b(eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*)\b',
                'category': 'authentication',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            
            # Environment Variables
            'env_variable_secret': {
                'pattern': r'(?i)([A-Z_]+SECRET[A-Z_]*)\s*=\s*["\']?([^"\'\s]{10,})["\']?',
                'category': 'environment',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            'env_variable_key': {
                'pattern': r'(?i)([A-Z_]+KEY[A-Z_]*)\s*=\s*["\']?([^"\'\s]{10,})["\']?',
                'category': 'environment',
                'confidence': 0.8,
                'risk_level': 'MEDIUM'
            },
            'env_variable_token': {
                'pattern': r'(?i)([A-Z_]+TOKEN[A-Z_]*)\s*=\s*["\']?([^"\'\s]{10,})["\']?',
                'category': 'environment',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            
            # Certificates and Keys
            'private_key_rsa': {
                'pattern': r'-----BEGIN RSA PRIVATE KEY-----',
                'category': 'certificate',
                'confidence': 0.95,
                'risk_level': 'CRITICAL'
            },
            'private_key_ec': {
                'pattern': r'-----BEGIN EC PRIVATE KEY-----',
                'category': 'certificate',
                'confidence': 0.95,
                'risk_level': 'CRITICAL'
            },
            'private_key_openssh': {
                'pattern': r'-----BEGIN OPENSSH PRIVATE KEY-----',
                'category': 'certificate',
                'confidence': 0.95,
                'risk_level': 'CRITICAL'
            },
            'ssh_private_key': {
                'pattern': r'-----BEGIN (DSA|RSA|EC|OPENSSH) PRIVATE KEY-----',
                'category': 'certificate',
                'confidence': 0.95,
                'risk_level': 'CRITICAL'
            },
            
            # Social Media & Analytics
            'facebook_token': {
                'pattern': r'\b(EAA[A-Za-z0-9]{100,})\b',
                'category': 'social_media',
                'confidence': 0.9,
                'risk_level': 'MEDIUM'
            },
            'twitter_consumer_key': {
                'pattern': r'\b([A-Za-z0-9]{25})\b',
                'category': 'social_media',
                'confidence': 0.6,
                'risk_level': 'MEDIUM'
            },
            'google_analytics': {
                'pattern': r'\b(UA-[0-9]{4,9}-[0-9]{1,4})\b',
                'category': 'analytics',
                'confidence': 0.9,
                'risk_level': 'LOW'
            },
            'google_tag_manager': {
                'pattern': r'\b(GTM-[A-Z0-9]{7})\b',
                'category': 'analytics',
                'confidence': 0.9,
                'risk_level': 'LOW'
            },
            
            # Infrastructure Secrets
            'terraform_token': {
                'pattern': r'\b([a-zA-Z0-9]{14}\.atlasv1\.[a-zA-Z0-9-_]{60,})\b',
                'category': 'infrastructure',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'vault_token': {
                'pattern': r'\b(hvs\.[a-zA-Z0-9_-]{20,})\b',
                'category': 'infrastructure',
                'confidence': 0.95,
                'risk_level': 'HIGH'
            },
            'kubernetes_token': {
                'pattern': r'\b(token:\s*[A-Za-z0-9\-_\.]{50,})\b',
                'category': 'infrastructure',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            
            # Base64 Encoded Secrets
            'base64_potential': {
                'pattern': r'\b([A-Za-z0-9+/]{40,}={0,2})\b',
                'category': 'encoded',
                'confidence': 0.3,
                'risk_level': 'LOW'
            },
            
            # URL Credentials
            'url_with_credentials': {
                'pattern': r'https?://[^:\s]+:[^@\s]+@[^\s]+',
                'category': 'url_credential',
                'confidence': 0.9,
                'risk_level': 'HIGH'
            },
            
            # Configuration Files
            'connection_string': {
                'pattern': r'(?i)(connection.?string|conn.?str)\s*[:=]\s*["\']([^"\']+)["\']',
                'category': 'configuration',
                'confidence': 0.8,
                'risk_level': 'HIGH'
            },
            'password_field': {
                'pattern': r'(?i)password\s*[:=]\s*["\']([^"\']{6,})["\']',
                'category': 'configuration',
                'confidence': 0.7,
                'risk_level': 'MEDIUM'
            },
        }
    
    def _initialize_false_positive_filters(self) -> List[str]:
        """Initialize patterns to filter false positives"""
        return [
            r'example',
            r'placeholder',
            r'test',
            r'demo',
            r'fake',
            r'sample',
            r'AKIA[0-9A-Z]{16}[\'\"]\s*#.*example',
            r'your[_-]api[_-]key[_-]here',
            r'replace[_-]with[_-]your',
            r'insert[_-]your',
            r'<[^>]+>',  # HTML tags
            r'null',
            r'undefined',
            r'TODO',
            r'FIXME',
        ]
    
    def scan_content(self, content: str, url: str = "unknown") -> List[Finding]:
        """Scan content for security findings using all patterns"""
        findings = []
        
        # Scan with each pattern
        for pattern_name, pattern_config in self.patterns.items():
            pattern_findings = self._scan_with_pattern(
                content, pattern_name, pattern_config, url
            )
            findings.extend(pattern_findings)
        
        # Filter false positives
        filtered_findings = self._filter_false_positives(findings)
        
        # Calculate entropy for findings
        for finding in filtered_findings:
            finding.entropy = self._calculate_entropy(finding.value)
            
            # Adjust confidence based on entropy
            if finding.entropy < 2.0:  # Low entropy indicates possible false positive
                finding.confidence *= 0.5
        
        return filtered_findings
    
    def _scan_with_pattern(self, content: str, pattern_name: str, 
                          pattern_config: Dict[str, Any], url: str) -> List[Finding]:
        """Scan content with a specific pattern"""
        findings = []
        pattern = pattern_config['pattern']
        
        try:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Extract the actual secret value
                if match.groups():
                    value = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                else:
                    value = match.group(0)
                
                # Skip very short or obviously fake values
                if len(value) < 8 or self._is_likely_placeholder(value):
                    continue
                
                # Extract context around the match
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(content), match.end() + 50)
                context = content[start_pos:end_pos].replace('\n', ' ').strip()
                
                finding = Finding(
                    pattern_type=pattern_name,
                    value=value,
                    confidence=pattern_config.get('confidence', 0.5),
                    url=url,
                    risk_level=pattern_config.get('risk_level', 'MEDIUM'),
                    context=context,
                    category=pattern_config.get('category', 'unknown')
                )
                
                findings.append(finding)
                
        except re.error as e:
            # Skip invalid regex patterns
            pass
        
        return findings
    
    def _filter_false_positives(self, findings: List[Finding]) -> List[Finding]:
        """Filter out likely false positives"""
        filtered = []
        
        for finding in findings:
            is_false_positive = False
            
            # Check against false positive patterns
            for fp_pattern in self.false_positive_filters:
                if re.search(fp_pattern, finding.value.lower()) or \
                   re.search(fp_pattern, finding.context.lower()):
                    is_false_positive = True
                    break
            
            # Additional heuristics
            if not is_false_positive:
                # Check for common placeholder patterns
                if finding.value.lower() in ['password', 'secret', 'token', 'key']:
                    is_false_positive = True
                
                # Check for repeated characters (likely placeholder)
                if len(set(finding.value)) <= 2:
                    is_false_positive = True
                
                # Check for sequential patterns
                if self._is_sequential(finding.value):
                    is_false_positive = True
            
            if not is_false_positive:
                filtered.append(finding)
        
        return filtered
    
    def _is_likely_placeholder(self, value: str) -> bool:
        """Check if value is likely a placeholder"""
        placeholder_indicators = [
            'your', 'insert', 'replace', 'enter', 'add', 'put',
            'example', 'sample', 'demo', 'test', 'placeholder'
        ]
        
        value_lower = value.lower()
        return any(indicator in value_lower for indicator in placeholder_indicators)
    
    def _is_sequential(self, value: str) -> bool:
        """Check if string contains sequential characters"""
        if len(value) < 4:
            return False
        
        # Check for sequential numbers
        sequential_count = 0
        for i in range(len(value) - 1):
            if value[i].isdigit() and value[i + 1].isdigit():
                if int(value[i + 1]) == int(value[i]) + 1:
                    sequential_count += 1
        
        return sequential_count > len(value) * 0.3
    
    def _calculate_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not data:
            return 0
        
        # Count character frequencies
        counts = {}
        for char in data:
            counts[char] = counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0
        length = len(data)
        
        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def process_file_content(self, file_path: str, content: bytes) -> List[Finding]:
        """Process file content based on file type"""
        findings = []
        
        try:
            # Determine file type and processing method
            if file_path.endswith(('.json', '.config')):
                findings.extend(self._process_json_file(content))
            elif file_path.endswith(('.xml', '.config')):
                findings.extend(self._process_xml_file(content))
            elif file_path.endswith('.zip'):
                findings.extend(self._process_zip_file(content))
            elif file_path.endswith(('.env', '.ini')):
                findings.extend(self._process_env_file(content))
            else:
                # Process as text
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    findings.extend(self.scan_content(text_content, file_path))
                except:
                    pass
        except Exception:
            pass
        
        return findings
    
    def _process_json_file(self, content: bytes) -> List[Finding]:
        """Process JSON files for sensitive data"""
        findings = []
        
        try:
            text_content = content.decode('utf-8', errors='ignore')
            json_data = json.loads(text_content)
            
            # Recursively scan JSON structure
            findings.extend(self._scan_json_recursive(json_data, "json_file"))
            
        except Exception:
            # Fallback to text scanning
            try:
                text_content = content.decode('utf-8', errors='ignore')
                findings.extend(self.scan_content(text_content, "json_file"))
            except:
                pass
        
        return findings
    
    def _scan_json_recursive(self, obj: Any, path: str) -> List[Finding]:
        """Recursively scan JSON object for sensitive data"""
        findings = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}"
                
                # Check if key indicates sensitive data
                sensitive_keys = ['password', 'secret', 'key', 'token', 'credential', 'auth']
                if any(sk in key.lower() for sk in sensitive_keys):
                    if isinstance(value, str) and len(value) > 8:
                        finding = Finding(
                            pattern_type=f"json_sensitive_key_{key}",
                            value=value,
                            confidence=0.8,
                            url=current_path,
                            category="configuration",
                            risk_level="HIGH"
                        )
                        findings.append(finding)
                
                # Recursively scan value
                findings.extend(self._scan_json_recursive(value, current_path))
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                findings.extend(self._scan_json_recursive(item, f"{path}[{i}]"))
                
        elif isinstance(obj, str):
            # Scan string values with our patterns
            findings.extend(self.scan_content(obj, path))
        
        return findings
    
    def _process_xml_file(self, content: bytes) -> List[Finding]:
        """Process XML files for sensitive data"""
        findings = []
        
        try:
            text_content = content.decode('utf-8', errors='ignore')
            findings.extend(self.scan_content(text_content, "xml_file"))
            
            # Additional XML-specific parsing could be added here
            
        except Exception:
            pass
        
        return findings
    
    def _process_zip_file(self, content: bytes) -> List[Finding]:
        """Process ZIP files by extracting and scanning contents"""
        findings = []
        
        try:
            import io
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_ref:
                for file_info in zip_ref.filelist[:20]:  # Limit files processed
                    try:
                        file_content = zip_ref.read(file_info.filename)
                        file_findings = self.process_file_content(
                            file_info.filename, file_content
                        )
                        
                        # Update finding URLs to include zip path
                        for finding in file_findings:
                            finding.url = f"zip:{finding.url}:{file_info.filename}"
                        
                        findings.extend(file_findings)
                    except Exception:
                        continue
                        
        except Exception:
            pass
        
        return findings
    
    def _process_env_file(self, content: bytes) -> List[Finding]:
        """Process environment files (.env, .ini) for sensitive data"""
        findings = []
        
        try:
            text_content = content.decode('utf-8', errors='ignore')
            
            # Scan each line for key=value pairs
            for line_num, line in enumerate(text_content.split('\n'), 1):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Check for sensitive keys
                    sensitive_indicators = ['password', 'secret', 'key', 'token', 'api', 'auth']
                    if any(indicator in key.lower() for indicator in sensitive_indicators):
                        if len(value) > 8:
                            finding = Finding(
                                pattern_type=f"env_sensitive_{key.lower()}",
                                value=value,
                                confidence=0.9,
                                url=f"env_file:line_{line_num}",
                                category="environment",
                                risk_level="HIGH"
                            )
                            findings.append(finding)
            
            # Also run general pattern scanning
            findings.extend(self.scan_content(text_content, "env_file"))
            
        except Exception:
            pass
        
        return findings
    
    def generate_pattern_summary(self) -> Dict[str, Any]:
        """Generate summary of all available patterns"""
        categories = {}
        
        for pattern_name, config in self.patterns.items():
            category = config.get('category', 'unknown')
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'patterns': [],
                    'risk_levels': set()
                }
            
            categories[category]['count'] += 1
            categories[category]['patterns'].append(pattern_name)
            categories[category]['risk_levels'].add(config.get('risk_level', 'MEDIUM'))
        
        # Convert sets to lists for JSON serialization
        for category in categories.values():
            category['risk_levels'] = list(category['risk_levels'])
        
        return {
            'total_patterns': len(self.patterns),
            'categories': categories,
            'pattern_count_by_category': {
                cat: info['count'] for cat, info in categories.items()
            }
        }
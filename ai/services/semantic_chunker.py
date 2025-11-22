"""
Semantic Chunking Service for Multilingual RAG Pipeline
Handles intelligent chunking of financial documents (loans, investments) with proper metadata extraction

FinTech RAG Pipeline - Universal Chunking & Metadata Extraction Methodology
- Semantic chunking by logical units (tables, FAQs, sections)
- Language detection and preservation
- Metadata normalization for precise filtering
"""
import re
from typing import Dict, List, Optional, Tuple
from langchain_core.documents import Document

from utils import logger


class SemanticChunker:
    """
    Semantic chunker that splits documents by logical sections rather than fixed character count.
    Handles tables, FAQs, and key sections intelligently.
    """
    
    # Scheme/Loan type normalization mappings
    SCHEME_MAPPINGS = {
        # English
        "national pension system": "NPS",
        "nps": "NPS",
        "public provident fund": "PPF",
        "ppf": "PPF",
        "sukanya samriddhi yojana": "SSY",
        "ssy": "SSY",
        # Hindi
        "नेशनल पेंशन सिस्टम": "NPS",
        "पब्लिक प्रोविडेंट फंड": "PPF",
        "सुकन्या समृद्धि योजना": "SSY",
    }
    
    LOAN_TYPE_MAPPINGS = {
        # English - Primary loan types (normalized to standard keys)
        "personal loan": "PERSONAL_LOAN",
        "व्यक्तिगत ऋण": "PERSONAL_LOAN",
        "home loan": "HOME_LOAN",
        "गृह ऋण": "HOME_LOAN",
        "auto loan": "AUTO_LOAN",
        "car loan": "AUTO_LOAN",
        "vehicle loan": "AUTO_LOAN",
        "वाहन ऋण": "AUTO_LOAN",
        "education loan": "EDUCATION_LOAN",
        "student loan": "EDUCATION_LOAN",
        "शिक्षा ऋण": "EDUCATION_LOAN",
        "gold loan": "GOLD_LOAN",
        "jewel loan": "GOLD_LOAN",
        "स्वर्ण ऋण": "GOLD_LOAN",
        "business loan": "BUSINESS_LOAN",
        "msme": "BUSINESS_LOAN",
        "mudra": "BUSINESS_LOAN",
        "व्यापार ऋण": "BUSINESS_LOAN",
        "loan against property": "LAP",
        "lap": "LAP",
        "संपत्ति पर ऋण": "LAP",
        # Sub-loan types (for business loans)
        "mudra loan": "BUSINESS_LOAN_MUDRA",
        "term loan": "BUSINESS_LOAN_TERM",
        "working capital": "BUSINESS_LOAN_WORKING_CAPITAL",
        "invoice financing": "BUSINESS_LOAN_INVOICE",
        "equipment financing": "BUSINESS_LOAN_EQUIPMENT",
        "business overdraft": "BUSINESS_LOAN_OVERDRAFT",
        # Sub-loan types (for home loans)
        "home purchase loan": "HOME_LOAN_PURCHASE",
        "home construction loan": "HOME_LOAN_CONSTRUCTION",
        "plot construction loan": "HOME_LOAN_PLOT_CONSTRUCTION",
        "home extension loan": "HOME_LOAN_EXTENSION",
        "home renovation loan": "HOME_LOAN_RENOVATION",
        "balance transfer loan": "HOME_LOAN_BALANCE_TRANSFER",
    }
    
    # Section headers in English and Hindi - normalized to English for metadata
    SECTION_PATTERNS = {
        "Overview": [r"PRODUCT OVERVIEW", r"OVERVIEW", r"उत्पाद अवलोकन", r"अवलोकन"],
        "Features": [r"KEY FEATURES", r"FEATURES", r"मुख्य विशेषताएं", r"विशेषताएं"],
        "Types": [r"TYPES OF", r"TYPES", r"प्रकार", r"के प्रकार"],
        "Eligibility": [r"ELIGIBILITY", r"ELIGIBILITY CRITERIA", r"पात्रता", r"पात्रता मानदंड"],
        "Documents": [r"DOCUMENTS REQUIRED", r"DOCUMENTS", r"दस्तावेज", r"आवश्यक दस्तावेज"],
        "Interest_Rates": [r"INTEREST RATE", r"INTEREST RATE STRUCTURE", r"RATE", r"ब्याज दर", r"ब्याज दर संरचना"],
        "Fees": [r"FEES", r"FEES & CHARGES", r"CHARGES", r"शुल्क", r"चार्ज"],
        "Repayment": [r"REPAYMENT", r"REPAYMENT STRUCTURE", r"पुनर्भुगतान"],
        "FAQ": [r"FREQUENTLY ASKED QUESTIONS", r"FAQ", r"प्रश्न", r"सवाल"],
    }
    
    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 2000):
        """
        Initialize semantic chunker
        
        Args:
            min_chunk_size: Minimum chunk size in characters
            max_chunk_size: Maximum chunk size in characters
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
    
    def preprocess_text(self, text: str) -> str:
        """
        Global pre-processing: Remove noise, headers, footers
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove HTML/XML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove generic headers/footers (but keep if at start for context)
        # Common patterns: Page numbers, URLs, generic bank info
        lines = text.split('\n')
        cleaned_lines = []
        is_start = True
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip generic headers/footers (unless at document start)
            if not is_start:
                # Skip page numbers
                if re.match(r'^Page\s+\d+$', line_stripped, re.IGNORECASE):
                    continue
                # Skip URLs
                if re.match(r'^https?://', line_stripped):
                    continue
                # Skip generic bank footer patterns
                if re.match(r'^www\.sunnationalbank', line_stripped, re.IGNORECASE):
                    continue
                if re.match(r'^\d{4}-\d{3}-\d{4}$', line_stripped):  # Phone numbers in footer
                    continue
            
            cleaned_lines.append(line)
            # After first few lines, mark as not start
            if len(cleaned_lines) > 3:
                is_start = False
        
        return '\n'.join(cleaned_lines)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text (English or Hindi)
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code: "en" or "hi"
        """
        # Simple heuristic: if text contains Devanagari characters, it's Hindi
        devanagari_pattern = r'[\u0900-\u097F]'
        if re.search(devanagari_pattern, text):
            return "hi"
        return "en"
    
    def normalize_scheme_or_loan_type(self, text: str, document_type: str = "loan", section_text: str = "") -> str:
        """
        Normalize scheme or loan type to standard acronym/identifier
        
        Args:
            text: Text containing scheme/loan name
            document_type: "loan" or "investment"
            section_text: Optional section text to detect sub-loan types
            
        Returns:
            Normalized identifier (e.g., "PPF", "HOME_LOAN", "BUSINESS_LOAN_MUDRA")
        """
        # Normalize text: replace underscores/spaces with spaces, remove file extensions
        text_normalized = text.lower().strip()
        text_normalized = text_normalized.replace("_", " ").replace("-", " ")
        text_normalized = text_normalized.replace(".pdf", "").replace("_product_guide", "").replace("_scheme_guide", "")
        text_normalized = text_normalized.replace("product guide", "").replace("scheme guide", "").strip()
        
        text_lower = text_normalized
        section_lower = section_text.lower() if section_text else ""
        combined_text = f"{text_lower} {section_lower}"
        
        if document_type == "investment":
            # Check scheme mappings (case-insensitive)
            for key, value in self.SCHEME_MAPPINGS.items():
                if key.lower() in text_lower:
                    return value  # Returns uppercase: PPF, NPS, SSY
            # Fallback: if filename is like "ppf_scheme_guide", normalize to uppercase
            if text_lower in ["ppf", "nps", "ssy"]:
                return text_lower.upper()  # "ppf" -> "PPF"
        else:
            # Check sub-loan types first (more specific) - check both text and section
            sub_loan_keywords = {
                "mudra": "BUSINESS_LOAN_MUDRA",
                "shishu": "BUSINESS_LOAN_MUDRA",
                "kishore": "BUSINESS_LOAN_MUDRA",
                "tarun": "BUSINESS_LOAN_MUDRA",
                "term loan": "BUSINESS_LOAN_TERM",
                "working capital": "BUSINESS_LOAN_WORKING_CAPITAL",
                "invoice financing": "BUSINESS_LOAN_INVOICE",
                "equipment financing": "BUSINESS_LOAN_EQUIPMENT",
                "business overdraft": "BUSINESS_LOAN_OVERDRAFT",
                "home purchase": "HOME_LOAN_PURCHASE",
                "home construction": "HOME_LOAN_CONSTRUCTION",
                "plot construction": "HOME_LOAN_PLOT_CONSTRUCTION",
                "plot + construction": "HOME_LOAN_PLOT_CONSTRUCTION",
                "home extension": "HOME_LOAN_EXTENSION",
                "home renovation": "HOME_LOAN_RENOVATION",
                "balance transfer": "HOME_LOAN_BALANCE_TRANSFER",
            }
            
            # Check for sub-loan types in combined text
            for keyword, value in sub_loan_keywords.items():
                if keyword in combined_text:
                    return value
            
            # Check main loan types - text_lower already has underscores normalized to spaces
            for key, value in self.LOAN_TYPE_MAPPINGS.items():
                # Check if key matches (text_lower already normalized, so "personal loan" will match)
                if key in text_lower and key not in sub_loan_keywords:
                    return value
        
        # Default fallback
        if document_type == "investment":
            return "UNKNOWN_SCHEME"
        return "UNKNOWN_LOAN"
    
    def extract_section_name(self, text: str) -> Optional[str]:
        """
        Extract section name from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Section name or None
        """
        for section, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return section.title().replace("_", " ")
        return None
    
    def detect_table(self, text: str) -> bool:
        """
        Detect if text contains a table
        
        Args:
            text: Text to check
            
        Returns:
            True if table detected
        """
        # Look for table indicators
        table_indicators = [
            r"The following table:",
            r"निम्नलिखित तालिका:",
            r"Feature.*Details",
            r"Criteria.*Requirement",
            r"Charge Type.*Amount",
            r"\|.*\|",  # Markdown table format
            r"विशेषता.*MUDRA",  # Hindi business loan table pattern
            r"MUDRA.*टर्म.*कार्यशील",  # Multiple loan types in header
        ]
        
        for indicator in table_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                return True
        
        # Check for CSV-style patterns (multiple lines with commas/quotes)
        lines = text.split('\n')
        if len(lines) >= 3:
            csv_pattern_count = sum(1 for line in lines[:5] if ',' in line and '"' in line)
            if csv_pattern_count >= 2:
                return True
        
        # Check for space-separated table with multiple columns (like business loan table)
        # Look for lines with multiple loan type names (MUDRA, Term, Working Capital, etc.)
        loan_type_keywords = ["mudra", "term", "working capital", "टर्म", "कार्यशील", "मुद्रा"]
        found_keywords = []
        for line in lines[:10]:  # Check first 10 lines
            line_lower = line.lower()
            for keyword in loan_type_keywords:
                if keyword in line_lower and keyword not in found_keywords:
                    found_keywords.append(keyword)
        # If we find 2+ loan type keywords in the same section, it's likely a comparison table
        if len(found_keywords) >= 2:
            return True
        
        return False
    
    def convert_table_to_markdown(self, text: str) -> str:
        """
        Convert table (CSV or space-separated) to Markdown format
        
        Args:
            text: Text containing table
            
        Returns:
            Markdown formatted table
        """
        lines = text.split('\n')
        markdown_lines = []
        in_table = False
        
        # First, try CSV format
        for line in lines:
            # Check if line looks like CSV table row
            if ',' in line and ('"' in line or any(char.isupper() for char in line[:50])):
                # Convert CSV row to markdown
                cells = [cell.strip().strip('"') for cell in line.split(',')]
                markdown_line = '| ' + ' | '.join(cells) + ' |'
                markdown_lines.append(markdown_line)
                in_table = True
            elif in_table and line.strip() == '':
                # Empty line ends table
                break
            elif not in_table:
                markdown_lines.append(line)
        
        # If no CSV table found, try space-separated table
        if not markdown_lines or '|' not in markdown_lines[-1]:
            markdown_lines = []
            # Look for space-separated table pattern
            # Pattern: Header row with multiple loan types, then data rows
            table_start_idx = None
            for i, line in enumerate(lines):
                # Check if this line contains multiple loan type keywords
                line_lower = line.lower()
                loan_keywords_found = sum(1 for kw in ["mudra", "term", "working", "टर्म", "कार्यशील", "मुद्रा"] if kw in line_lower)
                if loan_keywords_found >= 2:
                    table_start_idx = i
                    break
            
            if table_start_idx is not None:
                # Parse space-separated table
                # The table structure is: Feature | MUDRA | Term | Working Capital
                # We need to find column boundaries more intelligently
                header_line = lines[table_start_idx]
                
                # Look for known column headers in the header line
                # Pattern: "विशेषता" (Feature) followed by loan type names
                header_patterns = [
                    (r'विशेषता', 'Feature'),
                    (r'MUDRA[^\s]*', 'MUDRA लोन'),
                    (r'टर्म[^\s]*', 'SME टर्म लोन'),
                    (r'कार्यशील[^\s]*', 'कार्यशील पूंजी'),
                ]
                
                # Find positions of each header pattern
                header_positions = []
                for pattern, name in header_patterns:
                    match = re.search(pattern, header_line, re.IGNORECASE)
                    if match:
                        header_positions.append((match.start(), name))
                
                # Sort by position
                header_positions.sort(key=lambda x: x[0])
                
                if len(header_positions) >= 3:  # At least Feature + 2 loan types
                    # Extract column headers
                    header_cells = [pos[1] for pos in header_positions]
                    markdown_lines.append('| ' + ' | '.join(header_cells) + ' |')
                    markdown_lines.append('|' + '|'.join(['---'] * len(header_cells)) + '|')
                    
                    # For data rows, we'll use a simpler approach:
                    # Look for rows that start with known feature names (लोन राशि, ब्याज दर, etc.)
                    feature_keywords = ['लोन राशि', 'ब्याज दर', 'अवधि', 'गारंटी', 'प्रोसेसिंग']
                    
                    for line in lines[table_start_idx + 1:table_start_idx + 15]:  # Check next 15 lines
                        if not line.strip() or len(line.strip()) < 5:
                            continue
                        
                        # Check if this line starts with a feature keyword
                        is_data_row = any(line.strip().startswith(kw) for kw in feature_keywords)
                        if is_data_row:
                            # Try to extract cells by finding text between header positions
                            cells = []
                            for i, (pos, _) in enumerate(header_positions):
                                start_pos = pos
                                end_pos = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(line)
                                cell_text = line[start_pos:end_pos].strip()
                                cells.append(cell_text if cell_text else '')
                            
                            if len(cells) == len(header_cells):
                                markdown_lines.append('| ' + ' | '.join(cells) + ' |')
        
        if markdown_lines and '|' in markdown_lines[0]:
            # Ensure separator row exists
            if len(markdown_lines) > 1 and not markdown_lines[1].strip().startswith('|---'):
                header_idx = 0
                num_cols = markdown_lines[header_idx].count('|') - 1
                separator = '|' + '|'.join(['---'] * num_cols) + '|'
                markdown_lines.insert(1, separator)
        
        return '\n'.join(markdown_lines) if markdown_lines else text
    
    def extract_sub_loan_types_from_table(self, table_text: str, base_loan_type: str) -> List[str]:
        """
        Extract sub-loan types from a table that contains multiple loan type columns.
        
        For example, a table with columns: Feature | MUDRA Loan | Term Loan | Working Capital
        should return: [BUSINESS_LOAN_MUDRA, BUSINESS_LOAN_TERM, BUSINESS_LOAN_WORKING_CAPITAL]
        
        Args:
            table_text: Markdown table text or raw text
            base_loan_type: Base loan type (e.g., "BUSINESS_LOAN")
            
        Returns:
            List of detected sub-loan types
        """
        detected_sub_types = []
        
        # Map of column header patterns to sub-loan types
        sub_loan_column_patterns = {
            "business_loan": {
                "mudra": "BUSINESS_LOAN_MUDRA",
                "term loan": "BUSINESS_LOAN_TERM",
                "sme term": "BUSINESS_LOAN_TERM",
                "term": "BUSINESS_LOAN_TERM",  # Match "Term Loan" or "SME Term Loan"
                "working capital": "BUSINESS_LOAN_WORKING_CAPITAL",
                "invoice": "BUSINESS_LOAN_INVOICE",
                "equipment": "BUSINESS_LOAN_EQUIPMENT",
                "overdraft": "BUSINESS_LOAN_OVERDRAFT",
            },
            "home_loan": {
                "purchase": "HOME_LOAN_PURCHASE",
                "construction": "HOME_LOAN_CONSTRUCTION",
                "plot": "HOME_LOAN_PLOT_CONSTRUCTION",
                "extension": "HOME_LOAN_EXTENSION",
                "renovation": "HOME_LOAN_RENOVATION",
                "balance transfer": "HOME_LOAN_BALANCE_TRANSFER",
            }
        }
        
        base_type_lower = base_loan_type.lower().replace("_", " ")
        # Try both with space and underscore
        patterns = sub_loan_column_patterns.get(base_type_lower, {})
        if not patterns:
            # Try with underscore instead of space
            base_type_underscore = base_loan_type.lower()
            patterns = sub_loan_column_patterns.get(base_type_underscore, {})
        
        if not patterns:
            logger.warning(
                "no_patterns_for_loan_type",
                base_type=base_loan_type,
                base_type_lower=base_type_lower,
                available_keys=list(sub_loan_column_patterns.keys())
            )
            return []
        
        # Parse table to get column headers (handle both markdown and plain text)
        lines = table_text.split('\n')
        header_line = None
        
        # First, try to find header in markdown format
        for line in lines:
            line_lower = line.lower().strip()
            # Skip separator lines
            if line_lower.startswith('|---') or line_lower.startswith('---'):
                continue
            # Check if this looks like a header row
            if '|' in line:
                header_line = line
                break
        
        if header_line and '|' in header_line:
            # Extract column headers from markdown
            columns = [col.strip().lower() for col in header_line.split('|') if col.strip()]
            
            # Check each column header against sub-loan patterns
            for col_header in columns:
                # Skip "Feature" column
                if col_header in ["feature", "features", "criteria", "details", "विशेषता"]:
                    continue
                for pattern, sub_type in patterns.items():
                    if pattern in col_header:
                        if sub_type not in detected_sub_types:
                            detected_sub_types.append(sub_type)
                            logger.info(
                                "sub_loan_type_detected_in_table",
                                column_header=col_header,
                                pattern=pattern,
                                sub_type=sub_type
                            )
        else:
            # No markdown table found, search in raw text for loan type keywords
            # Handle multi-line headers where each column header is on a separate line
            # Pattern: "विशेषता" followed by loan type names on subsequent lines
            
            # Look for "विशेषता" or "Feature" which indicates start of table header
            feature_keywords = ["विशेषता", "feature", "features"]
            header_start_idx = None
            
            for i, line in enumerate(lines[:15]):
                line_lower = line.lower().strip()
                if any(kw in line_lower for kw in feature_keywords):
                    header_start_idx = i
                    break
            
            if header_start_idx is not None:
                # Check next few lines for loan type column headers
                # In space-separated tables, headers are often on consecutive lines
                header_lines = lines[header_start_idx:header_start_idx + 5]
                
                # Collect all loan type patterns found in header area
                found_patterns = []
                for line in header_lines:
                    line_lower = line.lower()
                    # Direct pattern matching for business loan sub-types
                    if ("mudra" in line_lower or "मुद्रा" in line) and "BUSINESS_LOAN_MUDRA" not in [p[1] for p in found_patterns]:
                        found_patterns.append(("mudra", "BUSINESS_LOAN_MUDRA"))
                    if (("term" in line_lower or "टर्म" in line) and 
                        "BUSINESS_LOAN_TERM" not in [p[1] for p in found_patterns]):
                        found_patterns.append(("term", "BUSINESS_LOAN_TERM"))
                    if (("working capital" in line_lower or "कार्यशील" in line) and 
                        "BUSINESS_LOAN_WORKING_CAPITAL" not in [p[1] for p in found_patterns]):
                        found_patterns.append(("working capital", "BUSINESS_LOAN_WORKING_CAPITAL"))
                
                # If we found 2+ loan types in the header area, add them
                if len(found_patterns) >= 1:  # Changed to 1+ since headers are on separate lines
                    logger.info(
                        "found_multi_line_header_with_sub_types",
                        header_start_line=header_start_idx,
                        header_lines_preview=[l[:80] for l in header_lines[:5]],
                        patterns_found=found_patterns
                    )
                    for pattern, sub_type in found_patterns:
                        if sub_type not in detected_sub_types:
                            detected_sub_types.append(sub_type)
                            logger.info(
                                "sub_loan_type_detected_in_multi_line_header",
                                pattern=pattern,
                                sub_type=sub_type
                            )
            
            # Fallback: Also check for single-line headers (original logic)
            if not detected_sub_types:
                for i, line in enumerate(lines[:20]):
                    line_lower = line.lower()
                    found_patterns = []
                    
                    if "mudra" in line_lower or "मुद्रा" in line:
                        found_patterns.append(("mudra", "BUSINESS_LOAN_MUDRA"))
                    if "term" in line_lower or "टर्म" in line:
                        found_patterns.append(("term", "BUSINESS_LOAN_TERM"))
                    if "working capital" in line_lower or "कार्यशील" in line:
                        found_patterns.append(("working capital", "BUSINESS_LOAN_WORKING_CAPITAL"))
                    
                    if len(found_patterns) >= 2:  # Multiple types in one line
                        for pattern, sub_type in found_patterns:
                            if sub_type not in detected_sub_types:
                                detected_sub_types.append(sub_type)
                        break
        
        return detected_sub_types
    
    def split_table_by_sub_loan_types(self, table_text: str, base_loan_type: str, section_name: Optional[str], 
                                      metadata: Dict, language: str, document_type: str, 
                                      chunk_id_start: int) -> List[Document]:
        """
        Split a table into multiple chunks, one for each sub-loan type column.
        
        Args:
            table_text: Markdown table text
            base_loan_type: Base loan type (e.g., "BUSINESS_LOAN")
            section_name: Section name
            metadata: Base metadata
            language: Language code
            document_type: "loan" or "investment"
            chunk_id_start: Starting chunk ID
            
        Returns:
            List of Document chunks, one per sub-loan type
        """
        # Extract sub-loan types from table headers
        sub_types = self.extract_sub_loan_types_from_table(table_text, base_loan_type)
        
        logger.info(
            "sub_loan_extraction_result",
            base_type=base_loan_type,
            sub_types_found=sub_types,
            table_text_preview=table_text[:500],
            table_line_count=len(table_text.split('\n'))
        )
        
        if not sub_types:
            # No sub-types detected, return table as single chunk with base type
            logger.warning(
                "no_sub_loan_types_extracted",
                base_type=base_loan_type,
                table_preview=table_text[:300]
            )
            chunk_metadata = self._create_chunk_metadata(
                metadata, base_loan_type, language, section_name, document_type, chunk_id_start, table_text
            )
            chunk_metadata["is_table"] = True
            return [Document(page_content=table_text, metadata=chunk_metadata)]
        
        # Parse table to extract columns
        lines = table_text.split('\n')
        header_line_idx = None
        separator_line_idx = None
        
        for i, line in enumerate(lines):
            if '|' in line and not line.strip().startswith('|---'):
                if header_line_idx is None:
                    header_line_idx = i
            elif line.strip().startswith('|---'):
                separator_line_idx = i
                break
        
        if header_line_idx is None:
            # Can't parse table, return as single chunk
            chunk_metadata = self._create_chunk_metadata(
                metadata, base_loan_type, language, section_name, document_type, chunk_id_start, table_text
            )
            chunk_metadata["is_table"] = True
            return [Document(page_content=table_text, metadata=chunk_metadata)]
        
        # Extract header row
        header_cells = [cell.strip() for cell in lines[header_line_idx].split('|') if cell.strip()]
        
        # Find column indices for each sub-loan type
        sub_type_columns = {}
        for sub_type in sub_types:
            # Find which column header matches this sub-type
            for pattern, mapped_sub_type in {
                "mudra": "BUSINESS_LOAN_MUDRA",
                "term loan": "BUSINESS_LOAN_TERM",
                "sme term": "BUSINESS_LOAN_TERM",
                "working capital": "BUSINESS_LOAN_WORKING_CAPITAL",
                "invoice": "BUSINESS_LOAN_INVOICE",
                "equipment": "BUSINESS_LOAN_EQUIPMENT",
                "overdraft": "BUSINESS_LOAN_OVERDRAFT",
            }.items():
                if mapped_sub_type == sub_type:
                    # Find column index
                    for idx, header in enumerate(header_cells):
                        if pattern in header.lower():
                            sub_type_columns[sub_type] = idx
                            break
                    break
        
        # If we can't map columns precisely, create chunks with full table but different loan_type metadata
        # This ensures each sub-loan type is retrievable
        if not sub_type_columns:
            chunks = []
            for sub_type in sub_types:
                chunk_metadata = self._create_chunk_metadata(
                    metadata, sub_type, language, section_name, document_type, chunk_id_start + len(chunks), table_text
                )
                chunk_metadata["is_table"] = True
                chunk_metadata["contains_multiple_sub_types"] = True
                chunk_metadata["table_sub_types"] = ",".join(sub_types)
                chunks.append(Document(page_content=table_text, metadata=chunk_metadata))
            logger.info(
                "table_chunks_created_with_sub_types",
                base_type=base_loan_type,
                sub_types=sub_types,
                chunk_count=len(chunks)
            )
            return chunks
        
        # Create separate chunks for each sub-loan type
        # Each chunk contains: Feature column + the specific sub-loan type column
        chunks = []
        feature_col_idx = 0  # Assuming first column is "Feature"
        
        for sub_type, col_idx in sub_type_columns.items():
            # Build table with Feature column + this sub-loan type column
            sub_table_lines = []
            
            # Header: Feature | {Sub-type Name}
            sub_type_name = header_cells[col_idx] if col_idx < len(header_cells) else sub_type.replace("_", " ").title()
            sub_table_lines.append(f"| Feature | {sub_type_name} |")
            sub_table_lines.append("| --- | --- |")
            
            # Data rows: Extract Feature + this sub-type's data
            for line in lines[header_line_idx + 1:]:
                if '|' in line and not line.strip().startswith('|---'):
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if len(cells) > max(feature_col_idx, col_idx):
                        feature_val = cells[feature_col_idx] if feature_col_idx < len(cells) else ""
                        sub_type_val = cells[col_idx] if col_idx < len(cells) else ""
                        sub_table_lines.append(f"| {feature_val} | {sub_type_val} |")
            
            sub_table_text = '\n'.join(sub_table_lines)
            
            # Create chunk with this sub-loan type
            chunk_metadata = self._create_chunk_metadata(
                metadata, sub_type, language, section_name, document_type, chunk_id_start + len(chunks), sub_table_text
            )
            chunk_metadata["is_table"] = True
            chunk_metadata["extracted_from_multi_type_table"] = True
            chunks.append(Document(page_content=sub_table_text, metadata=chunk_metadata))
        
        return chunks
    
    def detect_faq(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect FAQ Q&A pairs in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (question, answer) tuples
        """
        faqs = []
        
        # Check if text contains FAQ section
        if not re.search(r'FREQUENTLY ASKED QUESTIONS|FAQ|प्रश्न', text, re.IGNORECASE):
            return faqs
        
        # Patterns for questions (more flexible)
        question_patterns = [
            r'<b>Q\d+[:\s]+(.*?)</b>',  # HTML format
            r'Q\d+[:\s]+(.*?)(?=\n|Q\d+|$)',
            r'प्रश्न\s*\d+[:\s]+(.*?)(?=\n|प्रश्न|$)',
            r'Q[:\s]+(.*?)(?=\n|Q|$)',
            r'(\d+\.\s*[^?]+\?)',  # Numbered questions ending with ?
        ]
        
        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                question = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
                # Find answer (text after question until next question or end)
                start_pos = match.end()
                # Look for next question pattern
                next_q_match = re.search(r'Q\d+|प्रश्न\s*\d+|\d+\.\s*[^?]+\?', text[start_pos:], re.IGNORECASE)
                if next_q_match:
                    answer = text[start_pos:start_pos + next_q_match.start()].strip()
                else:
                    # Take next few sentences or until end
                    remaining = text[start_pos:]
                    sentences = re.split(r'[.!?]\s+', remaining)
                    answer = '. '.join(sentences[:3]).strip()  # Take first 3 sentences
                
                # Clean up answer (remove HTML tags, extra whitespace)
                answer = re.sub(r'<[^>]+>', '', answer)
                answer = ' '.join(answer.split())
                
                # Filter out very short answers (likely false positives)
                if question and answer and len(answer) > 20:
                    faqs.append((question, answer))
        
        return faqs
    
    def extract_keywords(self, text: str, language: str) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text to analyze
            language: Language code ("en" or "hi")
            
        Returns:
            List of keywords
        """
        keywords = []
        
        # Extract numbers (interest rates, amounts, percentages)
        numbers = re.findall(r'\d+[.,]?\d*%?', text)
        keywords.extend(numbers[:5])  # Limit to 5 numbers
        
        # Extract key financial terms
        if language == "en":
            financial_terms = [
                r'\b(interest rate|loan amount|tenure|emi|processing fee|eligibility|documents|collateral)\b',
                r'\b(rs\.?\s*\d+|rupees?\s*\d+|₹\s*\d+)\b',
                r'\b(\d+\s*years?|\d+\s*months?)\b',
            ]
        else:
            financial_terms = [
                r'\b(ब्याज दर|लोन राशि|अवधि|पात्रता|दस्तावेज|गारंटी)\b',
                r'\b(रुपये?\s*\d+|₹\s*\d+)\b',
                r'\b(\d+\s*वर्ष|\d+\s*महीने?)\b',
            ]
        
        for pattern in financial_terms:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend([m[0] if isinstance(m, tuple) else m for m in matches[:3]])
        
        # Extract section names
        section = self.extract_section_name(text)
        if section:
            keywords.append(section.lower())
        
        # Remove duplicates and limit
        keywords = list(dict.fromkeys(keywords))[:10]
        return keywords
    
    def split_by_sections(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """
        Split text by logical sections, including sub-loan types
        
        Args:
            text: Text to split
            
        Returns:
            List of (section_text, section_name) tuples
        """
        sections = []
        
        # Find all section headers (including sub-loan types)
        section_markers = []
        
        # Standard section patterns
        for section_name, patterns in self.SECTION_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                    section_markers.append((match.start(), section_name, match.group(0)))
        
        # Detect sub-loan types (e.g., "1. MUDRA Loans:", "2. Term Loans:")
        sub_loan_patterns = [
            r'\d+\.\s*(MUDRA|Term|Working Capital|Invoice Financing|Equipment Financing|Business Overdraft)[^:]*:',
            r'\d+\.\s*(Home Purchase|Home Construction|Plot|Home Extension|Home Renovation|Balance Transfer)[^:]*:',
            r'\d+\.\s*(शिशु|किशोर|तरुण|MUDRA|टर्म|कार्यशील पूंजी)[^:]*:',
        ]
        
        for pattern in sub_loan_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                # Extract sub-loan type
                sub_loan_text = match.group(1).strip()
                section_markers.append((match.start(), "SubLoan", sub_loan_text))
        
        # Sort by position
        section_markers.sort(key=lambda x: x[0])
        
        if not section_markers:
            # No sections found, return entire text
            return [(text, None)]
        
        # Extract sections
        for i, (start_pos, section_name, section_header) in enumerate(section_markers):
            # Find end position (next section or end of text)
            if i + 1 < len(section_markers):
                end_pos = section_markers[i + 1][0]
            else:
                end_pos = len(text)
            
            section_text = text[start_pos:end_pos].strip()
            if section_text:
                # For sub-loans, create more specific section name
                if section_name == "SubLoan":
                    section_name = f"Types - {section_header}"
                sections.append((section_text, section_name))
        
        return sections
    
    def chunk_document(self, document: Document) -> List[Document]:
        """
        Chunk a single document semantically
        
        Args:
            document: LangChain Document object
            
        Returns:
            List of chunked Document objects with enriched metadata
        """
        # Global pre-processing: Remove noise, headers, footers
        text = self.preprocess_text(document.page_content)
        metadata = document.metadata.copy()
        
        # Detect language
        language = self.detect_language(text)
        
        # Determine document type
        document_type = metadata.get("document_type", "loan")
        
        # Extract loan/scheme type
        source = metadata.get("source", "")
        loan_type = metadata.get("loan_type", "")
        scheme_type = metadata.get("scheme_type", "")
        
        # Normalize loan/scheme type (will be refined per chunk based on content)
        # Use source filename if loan_type/scheme_type is not available
        base_normalized_type = None
        if document_type == "investment":
            base_normalized_type = self.normalize_scheme_or_loan_type(
                scheme_type or source, document_type
            )
        else:
            # Try loan_type first, then source filename, ensuring we get a valid type
            base_normalized_type = self.normalize_scheme_or_loan_type(
                loan_type or source, document_type
            )
            # If still UNKNOWN, try with just the source filename (without path)
            if base_normalized_type == "UNKNOWN_LOAN" and source:
                # Extract just the filename without extension and normalize
                filename = source.replace(".pdf", "").replace("_product_guide", "").replace("_scheme_guide", "")
                # Try normalization again with cleaned filename
                base_normalized_type = self.normalize_scheme_or_loan_type(
                    filename, document_type
                )
                # Final fallback: if still UNKNOWN, try direct matching on cleaned filename
                if base_normalized_type == "UNKNOWN_LOAN":
                    filename_clean = filename.replace("_", " ").lower().strip()
                    # Direct match against loan type mappings
                    for key, value in self.LOAN_TYPE_MAPPINGS.items():
                        if key in filename_clean:
                            base_normalized_type = value
                            break
        
        chunks = []
        chunk_id_counter = 1
        
        # Check if text contains a table (but don't return early - tables might be part of sections)
        # We'll handle tables within sections instead
        
        # Check for FAQs
        faqs = self.detect_faq(text)
        if faqs:
                # Group FAQs together
                faq_texts = []
                for q, a in faqs:
                    faq_texts.append(f"Q: {q}\nA: {a}")
                
                # Split FAQs into chunks if too long
                current_faq_chunk = []
                current_length = 0
                
                for faq_text in faq_texts:
                    if current_length + len(faq_text) > self.max_chunk_size and current_faq_chunk:
                        # Save current chunk
                        chunk_content = "\n\n".join(current_faq_chunk)
                        chunk_metadata = self._create_chunk_metadata(
                            metadata, base_normalized_type, language, "FAQ", document_type, chunk_id_counter, chunk_content
                        )
                        chunk_metadata["is_faq"] = True
                        chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                        chunk_id_counter += 1
                        current_faq_chunk = []
                        current_length = 0
                    
                    current_faq_chunk.append(faq_text)
                    current_length += len(faq_text)
                
                # Add remaining FAQs
                if current_faq_chunk:
                    chunk_content = "\n\n".join(current_faq_chunk)
                    chunk_metadata = self._create_chunk_metadata(
                        metadata, base_normalized_type, language, "FAQ", document_type, chunk_id_counter, chunk_content
                    )
                    chunk_metadata["is_faq"] = True
                    chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                    chunk_id_counter += 1
                
                return chunks
        
        # Check if entire document contains a table BEFORE splitting by sections
        # This handles cases where tables span multiple "sections" (like business loan comparison table)
        if self.detect_table(text) and document_type == "loan" and base_normalized_type in ["BUSINESS_LOAN", "HOME_LOAN"]:
            # Try to extract and split table from entire text
            table_text = self.convert_table_to_markdown(text)
            table_chunks = self.split_table_by_sub_loan_types(
                table_text, base_normalized_type, "Overview", metadata,
                language, document_type, chunk_id_counter
            )
            if len(table_chunks) > 1:
                # Successfully split into multiple sub-loan type chunks
                chunks.extend(table_chunks)
                chunk_id_counter += len(table_chunks)
                logger.info(
                    "table_split_from_full_text",
                    base_type=base_normalized_type,
                    sub_types=[c.metadata.get("loan_type") for c in table_chunks],
                    chunk_count=len(table_chunks)
                )
                # Continue with remaining text (non-table content)
                # For now, we'll process the rest normally
                # TODO: Could extract non-table content and process separately
        
        # Split by logical sections
        sections = self.split_by_sections(text)
        
        for section_text, section_name in sections:
            # For tables, we want to detect sub-loan types from the table itself
            # So we should NOT refine the type before checking for tables
            # Check if this section contains a table FIRST
            if self.detect_table(section_text):
                # Keep base type for table processing - we'll split by sub-types from table headers
                normalized_type = base_normalized_type
                logger.info(
                    "table_detected",
                    section=section_name,
                    base_type=normalized_type,
                    section_length=len(section_text),
                    preview=section_text[:200]
                )
                
                # Check if table contains multiple sub-loan types BEFORE converting
                # Extract directly from raw text for better accuracy
                if document_type == "loan" and normalized_type in ["BUSINESS_LOAN", "HOME_LOAN"]:
                    # Extract sub-loan types directly from raw section text
                    sub_types_from_raw = self.extract_sub_loan_types_from_table(section_text, normalized_type)
                    
                    if sub_types_from_raw:
                        logger.info(
                            "sub_loan_types_found_in_raw_table",
                            base_type=normalized_type,
                            sub_types=sub_types_from_raw,
                            section_preview=section_text[:300]
                        )
                        # Convert to markdown first, then split by sub-loan types
                        # This ensures each chunk contains only the relevant column data
                        table_markdown = self.convert_table_to_markdown(section_text)
                        
                        # Split table into separate chunks for each sub-loan type
                        # Each chunk will contain only Feature + that sub-type's column
                        table_chunks = self.split_table_by_sub_loan_types(
                            table_markdown, normalized_type, section_name, metadata, language, document_type, chunk_id_counter
                        )
                        
                        chunks.extend(table_chunks)
                        chunk_id_counter += len(table_chunks)
                        
                        logger.info(
                            "table_chunks_created_for_sub_types",
                            base_type=normalized_type,
                            sub_types=sub_types_from_raw,
                            chunk_count=len(table_chunks),
                            note="Each chunk contains only relevant column data"
                        )
                        continue
                
                # Convert table to markdown for single chunk fallback
                table_text = self.convert_table_to_markdown(section_text)
                
                # Fallback: Keep table as single chunk
                if len(table_text) >= self.min_chunk_size:
                    chunk_metadata = self._create_chunk_metadata(
                        metadata, normalized_type, language, section_name, document_type, chunk_id_counter, table_text
                    )
                    chunk_metadata["is_table"] = True
                    chunks.append(Document(page_content=table_text, metadata=chunk_metadata))
                    chunk_id_counter += 1
                continue
                
                # Fallback: Keep table as single chunk
                if len(table_text) >= self.min_chunk_size:
                    chunk_metadata = self._create_chunk_metadata(
                        metadata, normalized_type, language, section_name, document_type, chunk_id_counter, table_text
                    )
                    chunk_metadata["is_table"] = True
                    chunks.append(Document(page_content=table_text, metadata=chunk_metadata))
                    chunk_id_counter += 1
                continue
            
            # Refine normalized type based on section content (for sub-loans)
            # Do this AFTER table processing, so tables can be split first
            normalized_type = base_normalized_type
            if document_type == "loan":
                refined_type = self.normalize_scheme_or_loan_type(
                    loan_type or source, document_type, section_text
                )
                # Only use refined type if it's more specific (not UNKNOWN)
                if refined_type != "UNKNOWN_LOAN" and refined_type != "UNKNOWN_SCHEME":
                    normalized_type = refined_type
            
            # Further split large sections
            if len(section_text) > self.max_chunk_size:
                # Split by paragraphs or sentences
                paragraphs = section_text.split('\n\n')
                current_chunk = []
                current_length = 0
                
                for para in paragraphs:
                    # Check if paragraph is a table
                    if self.detect_table(para):
                        # Save current chunk if exists
                        if current_chunk:
                            chunk_content = '\n\n'.join(current_chunk)
                            if len(chunk_content) >= self.min_chunk_size:
                                chunk_metadata = self._create_chunk_metadata(
                                    metadata, normalized_type, language, section_name, document_type, chunk_id_counter, chunk_content
                                )
                                chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                                chunk_id_counter += 1
                            current_chunk = []
                            current_length = 0
                        
                        # Handle table as separate chunk
                        table_text = self.convert_table_to_markdown(para)
                        if len(table_text) >= self.min_chunk_size:
                            chunk_metadata = self._create_chunk_metadata(
                                metadata, normalized_type, language, section_name, document_type, chunk_id_counter, table_text
                            )
                            chunk_metadata["is_table"] = True
                            chunks.append(Document(page_content=table_text, metadata=chunk_metadata))
                            chunk_id_counter += 1
                        continue
                    
                    if current_length + len(para) > self.max_chunk_size and current_chunk:
                        # Save current chunk
                        chunk_content = '\n\n'.join(current_chunk)
                        if len(chunk_content) >= self.min_chunk_size:
                            chunk_metadata = self._create_chunk_metadata(
                                metadata, normalized_type, language, section_name, document_type, chunk_id_counter, chunk_content
                            )
                            chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                            chunk_id_counter += 1
                        current_chunk = []
                        current_length = 0
                    
                    current_chunk.append(para)
                    current_length += len(para)
                
                # Add remaining content
                if current_chunk:
                    chunk_content = '\n\n'.join(current_chunk)
                    if len(chunk_content) >= self.min_chunk_size:
                        chunk_metadata = self._create_chunk_metadata(
                            metadata, normalized_type, language, section_name, document_type, chunk_id_counter, chunk_content
                        )
                        chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                        chunk_id_counter += 1
            else:
                # Section fits in one chunk
                if len(section_text) >= self.min_chunk_size:
                    chunk_metadata = self._create_chunk_metadata(
                        metadata, normalized_type, language, section_name, document_type, chunk_id_counter, section_text
                    )
                    chunks.append(Document(page_content=section_text, metadata=chunk_metadata))
                    chunk_id_counter += 1
        
        # If no sections found, split by paragraphs
        if not chunks:
            # Use base_normalized_type for fallback chunks
            normalized_type = base_normalized_type
            paragraphs = text.split('\n\n')
            current_chunk = []
            current_length = 0
            
            for para in paragraphs:
                if current_length + len(para) > self.max_chunk_size and current_chunk:
                    chunk_content = '\n\n'.join(current_chunk)
                    if len(chunk_content) >= self.min_chunk_size:
                        chunk_metadata = self._create_chunk_metadata(
                            metadata, normalized_type, language, None, document_type, chunk_id_counter, chunk_content
                        )
                        chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
                        chunk_id_counter += 1
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(para)
                current_length += len(para)
            
            if current_chunk:
                chunk_content = '\n\n'.join(current_chunk)
                if len(chunk_content) >= self.min_chunk_size:
                    chunk_metadata = self._create_chunk_metadata(
                        metadata, normalized_type, language, None, document_type, chunk_id_counter, chunk_content
                    )
                    chunks.append(Document(page_content=chunk_content, metadata=chunk_metadata))
        
        return chunks
    
    def _create_chunk_metadata(
        self,
        base_metadata: Dict,
        normalized_type: str,
        language: str,
        section: Optional[str],
        document_type: str,
        chunk_id: int,
        content: str = ""
    ) -> Dict:
        """
        Create enriched metadata for a chunk
        
        Args:
            base_metadata: Base metadata from document
            normalized_type: Normalized loan/scheme type
            language: Language code
            section: Section name
            document_type: "loan" or "investment"
            chunk_id: Chunk identifier number
            content: Chunk content (for keyword extraction)
            
        Returns:
            Enriched metadata dictionary
        """
        source = base_metadata.get("source", "unknown")
        source_base = source.replace(".pdf", "").replace("_product_guide", "").replace("_scheme_guide", "")
        
        # Create chunk ID following FinTech RAG format: "loan_type_lang_section_01"
        # Normalize section name for ID (use lowercase, replace spaces with underscores)
        section_for_id = (section or "general").lower().replace(" ", "_").replace("-", "_")
        chunk_id_str = f"{normalized_type.lower()}_{language}_{section_for_id}_{chunk_id:02d}"
        
        # Section name normalized to English for metadata (but keep original in content)
        section_display = section or "General"
        
        # Extract sub-loan type from section if available
        sub_loan_info = ""
        if section and "Types -" in section:
            sub_loan_info = section.replace("Types -", "").strip()
        
        # Create context header following FinTech RAG format
        # Format: "Loan Type - Section Name" (or with sub-loan info)
        # For Hindi: "Loan Type - Original Section (English Section)"
        if language == "hi":
            # For Hindi, include both Hindi and English in context header
            if sub_loan_info:
                context_header = f"{normalized_type} - {section_display} - {sub_loan_info}"
            else:
                # Get English equivalent for Hindi section
                section_english = self._get_english_section_name(section_display)
                if section_english and section_english != section_display:
                    context_header = f"{normalized_type} - {section_display} ({section_english})"
                else:
                    context_header = f"{normalized_type} - {section_display}"
        else:
            # English: Simple format
            if sub_loan_info:
                context_header = f"{normalized_type} - {section_display} - {sub_loan_info}"
            else:
                context_header = f"{normalized_type} - {section_display}"
        
        metadata = {
            **base_metadata,
            "id": chunk_id_str,
            "language": language,
            "section": section_display if section else "General",  # Normalized English section name
            "context_header": context_header,
        }
        
        # Set normalized loan_type or scheme_type (overwrite original lowercase values)
        if document_type == "investment":
            # Overwrite scheme_type with normalized uppercase (PPF, NPS, SSY)
            metadata["scheme_type"] = normalized_type
            # Also keep scheme for backward compatibility
            metadata["scheme"] = normalized_type
        else:
            # Overwrite loan_type with normalized uppercase (HOME_LOAN, PERSONAL_LOAN, etc.)
            metadata["loan_type"] = normalized_type
        
        # Add sub-loan info if available
        if sub_loan_info:
            metadata["sub_loan_type"] = sub_loan_info
        
        return metadata
    
    def _get_english_section_name(self, section_name: str) -> str:
        """
        Get English equivalent of Hindi section name for metadata normalization
        
        Args:
            section_name: Section name (may be in Hindi)
            
        Returns:
            English section name
        """
        # Map Hindi section names to English (normalized)
        hindi_to_english = {
            "पात्रता": "Eligibility",
            "पात्रता मानदंड": "Eligibility",
            "दस्तावेज": "Documents",
            "आवश्यक दस्तावेज": "Documents",
            "ब्याज दर": "Interest_Rates",
            "ब्याज दर संरचना": "Interest_Rates",
            "शुल्क": "Fees",
            "चार्ज": "Fees",
            "प्रश्न": "FAQ",
            "सवाल": "FAQ",
            "अवलोकन": "Overview",
            "उत्पाद अवलोकन": "Overview",
            "विशेषताएं": "Features",
            "मुख्य विशेषताएं": "Features",
        }
        
        for hindi, english in hindi_to_english.items():
            if hindi in section_name:
                return english
        
        # If no match, return as-is (already in English or unknown)
        return section_name
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        all_chunks = []
        
        for doc in documents:
            try:
                chunks = self.chunk_document(doc)
                all_chunks.extend(chunks)
                
                # Extract keywords for each chunk and convert to string (ChromaDB doesn't accept lists)
                for chunk in chunks:
                    keywords = self.extract_keywords(
                        chunk.page_content,
                        chunk.metadata.get("language", "en")
                    )
                    # Convert keywords list to comma-separated string for ChromaDB compatibility
                    chunk.metadata["keywords"] = ", ".join(keywords) if keywords else ""
                    
            except Exception as e:
                logger.error("chunking_error", error=str(e), source=doc.metadata.get("source", "unknown"))
                # Fallback: return original document
                all_chunks.append(doc)
        
        logger.info(
            "semantic_chunking_completed",
            original_count=len(documents),
            chunk_count=len(all_chunks)
        )
        
        return all_chunks


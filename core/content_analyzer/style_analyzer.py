"""
Style analyzer for analyzing writing style, tone, and readability.
"""

import re
from typing import Dict, Any, List
from .models import StyleAnalysis


class StyleAnalyzer:
    """Analyzer for writing style and readability."""
    
    def __init__(self):
        # Patterns for style analysis
        self.sentence_pattern = re.compile(r'[.!?]+')
        self.word_pattern = re.compile(r'\b\w+\b')
        self.passive_pattern = re.compile(r'\b(am|is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE)
        self.contraction_pattern = re.compile(r'\b\w+\'(t|ll|ve|re|d|s)\b', re.IGNORECASE)
        self.technical_pattern = re.compile(r'\b(algorithm|implementation|optimization|framework|architecture|protocol|interface|database|api|sdk|library|module|function|class|method|variable|parameter|configuration|deployment|infrastructure|microservice|container|kubernetes|docker|aws|azure|gcp|rest|graphql|oauth|jwt|ssl|tls|http|https|json|xml|yaml|sql|nosql|mongodb|postgresql|mysql|redis|elasticsearch|kafka|rabbitmq|nginx|apache|linux|unix|git|ci|cd|devops|agile|scrum|kanban|tdd|bdd|ddd|oop|fp|mvc|mvvm|mvp|poc|roi|kpi|api|sdk|ide|cli|gui|ui|ux|crud|orm|migration|backup|restore|monitoring|logging|analytics|metrics|dashboard|report|audit|security|authentication|authorization|encryption|hashing|salting|token|session|cookie|cache|cdn|load|balancing|scaling|performance|latency|throughput|bandwidth|memory|cpu|disk|network|storage|backup|recovery|disaster|recovery|high|availability|fault|tolerance|redundancy|replication|sharding|partitioning|indexing|query|optimization|transaction|consistency|isolation|durability|acid|base|cap|theorem|distributed|system|microservice|monolith|soa|event|driven|message|queue|stream|processing|batch|real|time|near|real|time|etl|elt|data|warehouse|data|lake|big|data|machine|learning|ai|nlp|computer|vision|deep|learning|neural|network|algorithm|model|training|inference|prediction|classification|regression|clustering|recommendation|system|search|engine|natural|language|processing|sentiment|analysis|text|mining|data|mining|statistics|probability|bayesian|frequentist|hypothesis|testing|confidence|interval|p|value|correlation|causation|regression|classification|clustering|dimensionality|reduction|feature|engineering|feature|selection|cross|validation|overfitting|underfitting|bias|variance|trade|off|ensemble|bagging|boosting|random|forest|gradient|boosting|svm|knn|naive|bayes|decision|tree|logistic|regression|linear|regression|polynomial|regression|ridge|regression|lasso|regression|elastic|net|regularization|normalization|standardization|scaling|encoding|one|hot|encoding|label|encoding|feature|scaling|min|max|scaling|z|score|normalization|outlier|detection|anomaly|detection|missing|data|imputation|data|cleaning|data|preprocessing|data|transformation|data|augmentation|data|synthesis|data|generation|data|simulation|data|visualization|chart|graph|plot|histogram|box|plot|scatter|plot|line|plot|bar|chart|pie|chart|heatmap|correlation|matrix|confusion|matrix|roc|curve|precision|recall|f1|score|accuracy|auc|mae|mse|rmse|mape|smape|r2|score|adjusted|r2|score|aic|bic|log|likelihood|information|criterion|entropy|gini|impurity|gain|ratio|chi|square|test|t|test|anova|f|test|z|test|wilcoxon|test|mann|whitney|test|kruskal|wallis|test|friedman|test|cochran|test|mcnemar|test|kappa|coefficient|pearson|correlation|spearman|correlation|kendall|correlation|point|biserial|correlation|phi|coefficient|cramer|v|coefficient|eta|squared|omega|squared|partial|eta|squared|effect|size|cohen|d|hedges|g|glass|delta|odds|ratio|risk|ratio|hazard|ratio|relative|risk|absolute|risk|attributable|risk|population|attributable|risk|number|needed|to|treat|number|needed|to|harm|likelihood|ratio|positive|likelihood|ratio|negative|likelihood|ratio|diagnostic|odds|ratio|sensitivity|specificity|positive|predictive|value|negative|predictive|value|false|positive|rate|false|negative|rate|true|positive|rate|true|negative|rate|receiver|operating|characteristic|area|under|curve|precision|recall|curve|f|beta|score|g|measure|matthews|correlation|coefficient|balanced|accuracy|cohen|kappa|weighted|kappa|quadratic|weighted|kappa|linear|weighted|kappa|fleiss|kappa|krippendorff|alpha|intraclass|correlation|coefficient|bland|altman|plot|bland|altman|limits|bland|altman|bias|bland|altman|agreement|limits|bland|altman|method|comparison|bland|altman|analysis|bland|altman|statistics|bland|altman|plot|bland|altman|limits|bland|altman|bias|bland|altman|agreement|limits|bland|altman|method|comparison|bland|altman|analysis|bland|altman|statistics)\b', re.IGNORECASE)
        
        # Tone indicators
        self.formal_indicators = [
            'furthermore', 'moreover', 'consequently', 'therefore', 'thus', 'hence',
            'accordingly', 'subsequently', 'nevertheless', 'nonetheless', 'notwithstanding',
            'in addition', 'in conclusion', 'in summary', 'as a result', 'for this reason'
        ]
        
        self.casual_indicators = [
            'hey', 'wow', 'cool', 'awesome', 'amazing', 'incredible', 'fantastic',
            'great', 'good', 'nice', 'sweet', 'perfect', 'excellent', 'brilliant',
            'genius', 'smart', 'clever', 'savvy', 'pro', 'expert', 'guru', 'ninja',
            'rockstar', 'wizard', 'master', 'champion', 'hero', 'legend', 'icon'
        ]
        
        self.technical_indicators = [
            'implementation', 'algorithm', 'optimization', 'framework', 'architecture',
            'protocol', 'interface', 'database', 'api', 'sdk', 'library', 'module',
            'function', 'class', 'method', 'variable', 'parameter', 'configuration'
        ]
    
    def analyze_style(self, content: str) -> StyleAnalysis:
        """Analyze writing style and generate comprehensive style analysis."""
        # Clean content for analysis
        clean_content = self._remove_markdown_formatting(content)
        
        # Analyze tone
        tone = self._analyze_tone(clean_content)
        
        # Analyze voice (active vs passive)
        voice = self._analyze_voice(clean_content)
        
        # Analyze sentence structure
        sentence_structure = self._analyze_sentence_structure(clean_content)
        
        # Analyze vocabulary level
        vocabulary_level = self._analyze_vocabulary_level(clean_content)
        
        # Calculate readability score
        readability_score = self._calculate_readability_score(clean_content)
        
        # Calculate style consistency
        style_consistency = self._calculate_style_consistency(clean_content)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(clean_content)
        
        # Generate style notes
        style_notes = self._generate_style_notes(clean_content, tone, voice, sentence_structure)
        
        return StyleAnalysis(
            tone=tone,
            voice=voice,
            sentence_structure=sentence_structure,
            vocabulary_level=vocabulary_level,
            readability_score=readability_score,
            style_consistency=style_consistency,
            engagement_score=engagement_score,
            style_notes=style_notes
        )
    
    def _remove_markdown_formatting(self, content: str) -> str:
        """Remove markdown formatting from content."""
        # Remove headers
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        # Remove bold/italic
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        # Remove inline code
        content = re.sub(r'`([^`]+)`', r'\1', content)
        # Remove links
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        # Remove images
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
        # Remove code blocks
        content = re.sub(r'```[\w]*\n.*?\n```', '', content, flags=re.DOTALL)
        # Remove blockquotes
        content = re.sub(r'^>\s*', '', content, flags=re.MULTILINE)
        # Remove list markers
        content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)
        
        return content
    
    def _analyze_tone(self, content: str) -> str:
        """Analyze the overall tone of the content."""
        content_lower = content.lower()
        
        # Count tone indicators
        formal_count = sum(1 for indicator in self.formal_indicators if indicator in content_lower)
        casual_count = sum(1 for indicator in self.casual_indicators if indicator in content_lower)
        technical_count = sum(1 for indicator in self.technical_indicators if indicator in content_lower)
        
        # Determine tone based on indicators
        if technical_count > 5:
            return "technical"
        elif formal_count > casual_count and formal_count > 2:
            return "formal"
        elif casual_count > formal_count and casual_count > 2:
            return "casual"
        elif formal_count == casual_count and formal_count > 0:
            return "mixed"
        else:
            return "neutral"
    
    def _analyze_voice(self, content: str) -> str:
        """Analyze whether content uses active or passive voice."""
        sentences = self.sentence_pattern.split(content)
        total_sentences = len([s for s in sentences if s.strip()])
        
        if total_sentences == 0:
            return "mixed"
        
        passive_sentences = len(self.passive_pattern.findall(content))
        passive_ratio = passive_sentences / total_sentences
        
        if passive_ratio > 0.3:
            return "passive"
        elif passive_ratio < 0.1:
            return "active"
        else:
            return "mixed"
    
    def _analyze_sentence_structure(self, content: str) -> str:
        """Analyze sentence structure complexity."""
        sentences = self.sentence_pattern.split(content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "simple"
        
        # Calculate average sentence length
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Count sentence length variations
        short_sentences = sum(1 for s in sentences if len(s.split()) <= 10)
        medium_sentences = sum(1 for s in sentences if 10 < len(s.split()) <= 20)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 20)
        
        total_sentences = len(sentences)
        
        if avg_length <= 12 and short_sentences / total_sentences > 0.6:
            return "simple"
        elif avg_length >= 20 and long_sentences / total_sentences > 0.4:
            return "complex"
        elif short_sentences > 0 and medium_sentences > 0 and long_sentences > 0:
            return "varied"
        else:
            return "moderate"
    
    def _analyze_vocabulary_level(self, content: str) -> str:
        """Analyze vocabulary complexity level."""
        words = self.word_pattern.findall(content.lower())
        
        if not words:
            return "basic"
        
        # Count complex words (7+ characters)
        complex_words = sum(1 for word in words if len(word) >= 7)
        complex_ratio = complex_words / len(words)
        
        # Count technical terms
        technical_terms = len(self.technical_pattern.findall(content))
        technical_ratio = technical_terms / len(words)
        
        if technical_ratio > 0.05:
            return "technical"
        elif complex_ratio > 0.3:
            return "advanced"
        elif complex_ratio > 0.15:
            return "intermediate"
        else:
            return "basic"
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate Flesch Reading Ease score."""
        sentences = self.sentence_pattern.split(content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        words = self.word_pattern.findall(content.lower())
        syllables = self._count_syllables(content)
        
        if len(words) == 0 or len(sentences) == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (approximate)."""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        # Adjust for common patterns
        if text.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        
        return count
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency score."""
        sentences = self.sentence_pattern.split(content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 1.0
        
        # Analyze sentence length consistency
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
        
        # Normalize consistency score
        consistency_score = max(0, 1 - (std_dev / avg_length))
        
        return round(consistency_score, 3)
    
    def _calculate_engagement_score(self, content: str) -> float:
        """Calculate engagement potential score."""
        score = 0.0
        
        # Check for questions (engagement indicator)
        question_count = content.count('?')
        if question_count > 0:
            score += min(0.2, question_count * 0.05)
        
        # Check for exclamations (engagement indicator)
        exclamation_count = content.count('!')
        if exclamation_count > 0:
            score += min(0.15, exclamation_count * 0.03)
        
        # Check for contractions (conversational tone)
        contraction_count = len(self.contraction_pattern.findall(content))
        if contraction_count > 0:
            score += min(0.1, contraction_count * 0.02)
        
        # Check for varied sentence structure
        sentences = self.sentence_pattern.split(content)
        if len(sentences) > 5:
            lengths = [len(s.split()) for s in sentences if s.strip()]
            if max(lengths) - min(lengths) > 10:
                score += 0.15
        
        # Check for active voice (more engaging)
        if self._analyze_voice(content) == "active":
            score += 0.2
        
        # Check for appropriate tone
        tone = self._analyze_tone(content)
        if tone in ["casual", "mixed"]:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_style_notes(self, content: str, tone: str, voice: str, sentence_structure: str) -> List[str]:
        """Generate style analysis notes."""
        notes = []
        
        # Tone notes
        if tone == "formal":
            notes.append("Uses formal language and academic tone")
        elif tone == "casual":
            notes.append("Uses casual, conversational language")
        elif tone == "technical":
            notes.append("Contains technical terminology and concepts")
        
        # Voice notes
        if voice == "passive":
            notes.append("Heavy use of passive voice - consider using active voice for clarity")
        elif voice == "active":
            notes.append("Good use of active voice for clarity and engagement")
        
        # Sentence structure notes
        if sentence_structure == "simple":
            notes.append("Uses simple, clear sentence structures")
        elif sentence_structure == "complex":
            notes.append("Uses complex sentence structures - consider breaking down long sentences")
        elif sentence_structure == "varied":
            notes.append("Good variety in sentence structure")
        
        # Readability notes
        readability = self._calculate_readability_score(content)
        if readability < 30:
            notes.append("Low readability score - consider simplifying language")
        elif readability > 70:
            notes.append("Good readability score")
        
        # Engagement notes
        engagement = self._calculate_engagement_score(content)
        if engagement < 0.3:
            notes.append("Low engagement potential - consider adding questions or varied structure")
        elif engagement > 0.7:
            notes.append("High engagement potential")
        
        return notes

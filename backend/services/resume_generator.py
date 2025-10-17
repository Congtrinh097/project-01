"""
resume_generator.py

Service for generating professional resumes using Hugging Face (via Featherless AI) or Mock mode.
Supports text input and structured profile JSON.

Author: AI Assistant
Date: 2025-10-11
"""

import os
import json
import textwrap
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)

# Optional: Try to import HuggingFace InferenceClient
try:
    from huggingface_hub import InferenceClient
    _HF_AVAILABLE = True
except Exception:
    _HF_AVAILABLE = False


class HuggingFaceModel:
    """
    Wrapper around Hugging Face InferenceClient using Featherless AI provider.
    Provides generate_text(prompt, ...) -> str
    """

    def __init__(self, model_name: str = settings.HF_MODEL_NAME):
        self.model_name = model_name
        self._client = None

        if not _HF_AVAILABLE:
            raise RuntimeError(
                "huggingface_hub is not installed. Install with: pip install huggingface_hub"
            )

        hf_token = settings.HF_TOKEN
        if not hf_token:
            raise RuntimeError(
                "HF_TOKEN environment variable not set. Please set your Hugging Face API token."
            )

        try:
            # Initialize the InferenceClient with token
            # Note: For Featherless AI, the token should be your Featherless API key
            self._client = InferenceClient(token=hf_token)
            logger.info(f"[HuggingFaceModel] Initialized InferenceClient with model: {model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Hugging Face client: {e}")

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        """
        Generate text using the Hugging Face model.
        Returns the generated string.
        """
        if self._client is None:
            raise RuntimeError("Hugging Face client not initialized.")
        try:
            result = self._client.text_generation(
                prompt,
                model=self.model_name,
                max_new_tokens=max_tokens,
                temperature=temperature,
            )
            
            if isinstance(result, str):
                return result.strip()
            return str(result).strip()
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            raise RuntimeError(f"Error during text generation: {e}")


class MockLlamaModel:
    """
    Simple fallback generator for testing and demonstration when LLaMA is not available.
    Uses template logic to produce deterministic resume text from the prompt/profile.
    """

    def __init__(self):
        logger.info("[MockLlamaModel] Running in MOCK mode (no LLaMA). Outputs are synthetic examples.")

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        # Attempt to extract a JSON-like "profile" from the prompt (we included it)
        try:
            start = prompt.find("<<PROFILE_JSON>>")
            if start != -1:
                end = prompt.find("<<END_PROFILE_JSON>>", start)
                if end != -1:
                    json_text = prompt[start + len("<<PROFILE_JSON>>"):end].strip()
                    profile = json.loads(json_text)
                    return self._render_resume_from_profile(profile)
        except Exception:
            pass
        
        # If no structured data, try to extract from text input
        return self._render_from_text(prompt)

    def _render_from_text(self, text: str) -> str:
        """Generate resume from plain text input"""
        lines = []
        lines.append("PROFESSIONAL RESUME")
        lines.append("=" * 80)
        lines.append("\nPROFESSIONAL SUMMARY")
        lines.append("-" * 80)
        
        # Extract key information from text
        text_preview = text[:500] if len(text) > 500 else text
        lines.append(textwrap.fill(
            "Experienced professional with demonstrated expertise in delivering high-quality results. "
            "Strong analytical and problem-solving skills with attention to detail.",
            width=80
        ))
        
        lines.append("\n\nKEY QUALIFICATIONS")
        lines.append("-" * 80)
        lines.append("• Proven track record of success in professional environments")
        lines.append("• Strong communication and interpersonal skills")
        lines.append("• Adaptable and quick learner with passion for continuous improvement")
        lines.append("• Collaborative team player with leadership capabilities")
        
        lines.append("\n\nADDITIONAL INFORMATION")
        lines.append("-" * 80)
        lines.append(textwrap.fill(text_preview, width=80))
        
        return "\n".join(lines)

    def _render_resume_from_profile(self, p: dict) -> str:
        """Generate resume from structured profile"""
        name = p.get("name", "PROFESSIONAL")
        title = p.get("title", "")
        summary = p.get("summary", "")
        experiences = p.get("experience", [])
        education = p.get("education", [])
        skills = p.get("skills", [])

        lines = []
        lines.append(f"{name}".upper())
        if title:
            lines.append(f"{title}")
        lines.append("=" * 80)
        
        if summary:
            lines.append("\nPROFESSIONAL SUMMARY")
            lines.append("-" * 80)
            lines.append(textwrap.fill(summary, width=80))
        
        if experiences:
            lines.append("\n\nPROFESSIONAL EXPERIENCE")
            lines.append("-" * 80)
            for exp in experiences:
                role = exp.get('role', 'Role')
                company = exp.get('company', '')
                years = exp.get('years', '')
                lines.append(f"\n{role}")
                lines.append(f"{company} | {years}")
                if exp.get("bullets"):
                    for b in exp.get("bullets"):
                        lines.append(f"  • {b}")
        
        if education:
            lines.append("\n\nEDUCATION")
            lines.append("-" * 80)
            for ed in education:
                degree = ed.get('degree', '')
                institution = ed.get('institution', '')
                year = ed.get('year', '')
                lines.append(f"{degree}")
                lines.append(f"{institution} | {year}")
                lines.append("")
        
        if skills:
            lines.append("\nSKILLS")
            lines.append("-" * 80)
            lines.append(", ".join(skills))
        
        return "\n".join(lines)


class ResumeGenerator:
    """
    High-level resume generator. Prepares prompts, calls the model, and post-processes outputs.
    """

    def __init__(self):
        """
        Initialize the resume generator with either Hugging Face or Mock model
        """
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the appropriate model (Hugging Face or Mock)"""
        model_name = os.environ.get("HF_MODEL_NAME", "meta-llama/Llama-3.1-8B")
        
        try:
            if _HF_AVAILABLE and settings.HF_TOKEN:
                logger.info("Attempting to load Hugging Face model...")
                self.model = HuggingFaceModel(model_name=model_name)
                logger.info(f"Hugging Face model loaded successfully: {model_name}")
            else:
                raise RuntimeError("Hugging Face not available or HF_TOKEN not set")
        except Exception as e:
            logger.warning(f"Hugging Face initialization failed: {e}")
            logger.info("Falling back to MockLlamaModel")
            self.model = MockLlamaModel()

    @staticmethod
    def _build_prompt_from_text(text: str) -> str:
        """
        Craft a prompt for the model from plain text input.
        """
        instructions = textwrap.dedent(
            """
            You are a professional resume writer. Generate a clean, concise, and ATS-friendly resume in plain text.
            Requirements:
             - Use sections: Header, Professional Summary, Experience (reverse chronological), Education, Skills.
             - Use bullet points for achievements.
             - Keep length roughly 1 page for mid-level profiles, up to 2 pages for senior.
             - Favor action verbs and metrics where available.
             - Output only the resume text (no commentary).
            
            Based on the following information, create a professional resume:
            """
        ).strip()
        
        prompt = f"{instructions}\n\n{text}\n\nProduce the resume now:\n"
        return prompt

    @staticmethod
    def _build_prompt_from_profile(profile: dict) -> str:
        """
        Craft a prompt for the model from structured profile JSON.
        """
        instructions = textwrap.dedent(
            """
            You are a professional resume writer. Generate a clean, concise, and ATS-friendly resume in plain text.
            Requirements:
             - Use sections: Header, Professional Summary, Experience (reverse chronological), Education, Skills.
             - Use bullet points for achievements.
             - Keep length roughly 1 page for mid-level profiles, up to 2 pages for senior.
             - Favor action verbs and metrics where available.
             - Output only the resume text (no commentary).
            """
        ).strip()

        profile_json = json.dumps(profile, ensure_ascii=False, indent=2)
        prompt = f"{instructions}\n\n<<PROFILE_JSON>>\n{profile_json}\n<<END_PROFILE_JSON>>\n\nProduce the resume now:\n"
        return prompt

    def generate_from_text(self, text: str, max_tokens: int = 800, temperature: float = 0.2) -> str:
        """
        Generate resume from plain text input.
        
        Args:
            text: Plain text containing resume information
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature (lower = more deterministic)
            
        Returns:
            Generated resume text
        """
        prompt = self._build_prompt_from_text(text)
        raw = self.model.generate_text(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
        resume_text = raw.strip()
        resume_text = resume_text.replace("<<PROFILE_JSON>>", "").replace("<<END_PROFILE_JSON>>", "")
        return resume_text

    def generate_from_profile(self, profile: dict, max_tokens: int = 800, temperature: float = 0.2) -> str:
        """
        Generate resume from structured profile dictionary.
        
        Args:
            profile: Dictionary containing structured resume data
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Generated resume text
        """
        prompt = self._build_prompt_from_profile(profile)
        raw = self.model.generate_text(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
        resume_text = raw.strip()
        resume_text = resume_text.replace("<<PROFILE_JSON>>", "").replace("<<END_PROFILE_JSON>>", "")
        return resume_text


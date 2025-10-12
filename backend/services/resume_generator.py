"""
resume_generator.py

Service for generating professional resumes using LLaMA3 (locally) or Mock mode.
Supports text input and structured profile JSON.

Author: AI Assistant
Date: 2025-10-11
"""

import os
import json
import textwrap
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Optional: Try to import Llama from llama_cpp
try:
    from llama_cpp import Llama  # type: ignore
    _LLAMA_AVAILABLE = True
except Exception:
    _LLAMA_AVAILABLE = False


class LlamaModel:
    """
    Wrapper around LLaMA via llama-cpp-python. Provides generate_text(prompt, ...) -> str
    Falls back to raising descriptive errors if LLaMA or model is unavailable.
    """

    def __init__(self, model_path: str, n_ctx: int = 2048):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self._llm = None

        if not _LLAMA_AVAILABLE:
            raise RuntimeError(
                "llama-cpp-python is not installed. Install with: pip install llama-cpp-python"
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        try:
            # initialize the llama model
            self._llm = Llama(model_path=model_path, n_ctx=n_ctx)
            logger.info(f"[LlamaModel] Loaded LLaMA model from: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLaMA: {e}")

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        """
        Generate text using the loaded model.
        Returns the generated string (decoded).
        """
        if self._llm is None:
            raise RuntimeError("LLaMA model not initialized.")
        try:
            resp = self._llm(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
            if isinstance(resp, dict) and 'choices' in resp and len(resp['choices']) > 0:
                return resp['choices'][0].get('text', '').strip()
            if hasattr(resp, 'choices') and len(resp.choices) > 0:
                return resp.choices[0].text.strip()
            return str(resp).strip()
        except Exception as e:
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
        Initialize the resume generator with either LLaMA or Mock model
        """
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the appropriate model (LLaMA or Mock)"""
        model_path = os.environ.get("MODEL_PATH", "./models/llama-2-7b-chat.Q4_K_M.gguf")
        
        try:
            if _LLAMA_AVAILABLE and os.path.exists(model_path):
                logger.info("Attempting to load LLaMA model...")
                self.model = LlamaModel(model_path=model_path)
                logger.info("LLaMA model loaded successfully")
            else:
                raise RuntimeError("LLaMA not available or model not found")
        except Exception as e:
            logger.warning(f"LLaMA initialization failed: {e}")
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


import logging
import json
from langchain_core.tools import tool
from database import SessionLocal
from models import Job

logger = logging.getLogger(__name__)


@tool
def get_total_jobs_count() -> str:
    """Returns the total number of jobs in the database as text."""
    session = None
    try:
        session = SessionLocal()
        total = session.query(Job).count()
        return str(total)
    except Exception as e:
        logger.error(f"Error counting jobs: {e}")
        return f"Error counting jobs: {str(e)}"
    finally:
        if session is not None:
            session.close()


@tool
def get_jobs_summary_by_technical_skills(top_n: int = 20) -> str:
    """Returns JSON with counts of jobs per technical skill.

    Args:
        top_n: Maximum number of skills to return, sorted by count desc.
    """
    session = None
    try:
        session = SessionLocal()
        rows = session.query(Job.technical_skills).all()

        skill_to_count = {}
        total_jobs = len(rows)

        for (skills,) in rows:
            if not skills:
                continue
            if isinstance(skills, list):
                iterable = skills
            else:
                iterable = []
            for skill in iterable:
                if not skill:
                    continue
                key = str(skill).strip().lower()
                if not key:
                    continue
                skill_to_count[key] = skill_to_count.get(key, 0) + 1

        sorted_counts = sorted(skill_to_count.items(), key=lambda kv: kv[1], reverse=True)
        if isinstance(top_n, int) and top_n > 0:
            sorted_counts = sorted_counts[:top_n]

        payload = {
            "total_jobs": total_jobs,
            "skills_count": [
                {"skill": name, "count": count} for name, count in sorted_counts
            ],
        }
        return json.dumps(payload, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error summarizing technical skills: {e}")
        return f"Error summarizing technical skills: {str(e)}"
    finally:
        if session is not None:
            session.close()



import logging
import json
from langchain_core.tools import tool
from database import SessionLocal
from models import Job
from .job_recommender import JobRecommender
from .cv_recommender import CVRecommender

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

@tool
def search_and_recommend_jobs(query: str, limit: int = 5) -> str:
    """Search and recommend jobs using semantic similarity and AI summary.

    Args:
        query: User search text or brief CV/profile summary.
        limit: Max number of job results to include.

    Returns:
        JSON string with keys: query, results, ai_recommendation.
    """
    import json
    session = None
    try:
        session = SessionLocal()
        recommender = JobRecommender()
        result = recommender.search_and_recommend(query=query, db=session, limit=limit)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"Error in search_and_recommend_jobs: {e}")
        return f"Error in search_and_recommend_jobs: {str(e)}"
    finally:
        if session is not None:
            session.close()

@tool
def search_and_recommend_cvs(query: str, limit: int = 5) -> str:
    """Search and recommend CVs or candidates using semantic similarity and AI summary.

    Args:
        query: Search text (skills/role/requirements) to match candidate CVs.
        limit: Max number of CV results to include.

    Returns:
        JSON string with keys: query, results, ai_recommendation.
    """
    import json
    session = None
    try:
        session = SessionLocal()
        recommender = CVRecommender()
        result = recommender.search_and_recommend(query=query, db=session, limit=limit)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"Error in search_and_recommend_cvs: {e}")
        return f"Error in search_and_recommend_cvs: {str(e)}"
    finally:
        if session is not None:
            session.close()



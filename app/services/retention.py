from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app import models


def delete_documents_older_than(db: Session, older_than_days: int, dry_run: bool = False) -> dict[str, int | bool]:
    if older_than_days < 1:
        raise ValueError("older_than_days must be at least 1")

    cutoff = (datetime.now(UTC) - timedelta(days=older_than_days)).replace(tzinfo=None)
    resume_ids = [row.id for row in db.query(models.Document.id).filter(models.Document.created_at < cutoff).all()]
    job_ids = [row.id for row in db.query(models.JobDescription.id).filter(models.JobDescription.created_at < cutoff).all()]
    analysis_query = db.query(models.Analysis.id)
    if resume_ids or job_ids:
        filters = []
        if resume_ids:
            filters.append(models.Analysis.resume_id.in_(resume_ids))
        if job_ids:
            filters.append(models.Analysis.job_description_id.in_(job_ids))
        from sqlalchemy import or_

        analysis_query = analysis_query.filter(or_(*filters))
    analysis_ids = [row.id for row in analysis_query.all()]

    result: dict[str, int | bool] = {
        "dry_run": dry_run,
        "resume_count": len(resume_ids),
        "job_description_count": len(job_ids),
        "analysis_count": len(analysis_ids),
    }
    if dry_run:
        return result

    if analysis_ids:
        db.query(models.SkillMatch).filter(models.SkillMatch.analysis_id.in_(analysis_ids)).delete(synchronize_session=False)
        db.query(models.GrowthGoal).filter(models.GrowthGoal.analysis_id.in_(analysis_ids)).delete(synchronize_session=False)
        db.query(models.Analysis).filter(models.Analysis.id.in_(analysis_ids)).delete(synchronize_session=False)
    if resume_ids:
        db.query(models.Document).filter(models.Document.id.in_(resume_ids)).delete(synchronize_session=False)
    if job_ids:
        db.query(models.JobDescription).filter(models.JobDescription.id.in_(job_ids)).delete(synchronize_session=False)
    db.commit()
    return result

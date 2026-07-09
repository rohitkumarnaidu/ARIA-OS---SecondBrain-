from fastapi import APIRouter, HTTPException, Depends
from database.schemas.feature_flag import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
)
from config.core.auth import get_current_user
from shared.utils.feature_flags import flags, FeatureFlag
from shared.utils.logger import logger
from datetime import datetime

router = APIRouter()


@router.get("/")
async def list_feature_flags(
    user_id: str = Depends(get_current_user),
):
    all_flags = flags.all_flags()
    return {
        "data": [
            {
                "key": key,
                "enabled": flag.enabled,
                "rollout_percentage": flag.rollout_percentage,
                "user_segments": flag.user_segments,
                "metadata": flag.metadata,
                "updated_at": flag.updated_at,
            }
            for key, flag in all_flags.items()
        ]
    }


@router.get("/{key}")
async def get_feature_flag(
    key: str,
    user_id: str = Depends(get_current_user),
):
    flag = flags._flags.get(key)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return {
        "key": flag.key,
        "enabled": flag.enabled,
        "rollout_percentage": flag.rollout_percentage,
        "user_segments": flag.user_segments,
        "metadata": flag.metadata,
        "updated_at": flag.updated_at,
    }


@router.get("/{key}/evaluate")
async def evaluate_feature_flag(
    key: str,
    user_id: str = Depends(get_current_user),
):
    enabled = flags.get(key, user_id=user_id, default=False)
    variant = flags.get_variant(key, user_id=user_id)
    return {"key": key, "enabled": enabled, "variant": variant}


@router.post("/", status_code=201)
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    user_id: str = Depends(get_current_user),
):
    existing = flags._flags.get(flag_data.key)
    if existing:
        raise HTTPException(status_code=409, detail="Flag already exists")
    new_flag = FeatureFlag(
        key=flag_data.key,
        enabled=flag_data.enabled,
        rollout_percentage=flag_data.rollout_percentage,
        user_segments=flag_data.user_segments,
        metadata=flag_data.metadata,
    )
    flags.set(flag_data.key, new_flag)
    logger.info("Feature flag created", key=flag_data.key)
    return new_flag.to_dict()


@router.put("/{key}")
async def update_feature_flag(
    key: str,
    flag_data: FeatureFlagUpdate,
    user_id: str = Depends(get_current_user),
):
    existing = flags._flags.get(key)
    if not existing:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    if flag_data.enabled is not None:
        existing.enabled = flag_data.enabled
    if flag_data.rollout_percentage is not None:
        existing.rollout_percentage = flag_data.rollout_percentage
    if flag_data.user_segments is not None:
        existing.user_segments = flag_data.user_segments
    if flag_data.metadata is not None:
        existing.metadata = flag_data.metadata
    existing.updated_at = datetime.utcnow().isoformat()
    flags.set(key, existing)
    logger.info("Feature flag updated", key=key)
    return existing.to_dict()


@router.delete("/{key}", status_code=204)
async def delete_feature_flag(
    key: str,
    user_id: str = Depends(get_current_user),
):
    if not flags.delete(key):
        raise HTTPException(status_code=404, detail="Feature flag not found")
    logger.info("Feature flag deleted", key=key)

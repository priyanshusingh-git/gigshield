from __future__ import annotations

import os
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency during local bootstrap
    OpenAI = None  # type: ignore[assignment]


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST_DIR = ROOT_DIR / "frontend" / "dist"
FRONTEND_INDEX_FILE = FRONTEND_DIST_DIR / "index.html"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


TIER_CONFIG: dict[str, dict[str, int]] = {
    "Saathi": {"base_premium": 20, "max_payout": 400},
    "Rakshak": {"base_premium": 45, "max_payout": 900},
    "Suraksha": {"base_premium": 80, "max_payout": 1600},
}

CITY_ZONE_RISK: dict[str, dict[str, float]] = {
    "Mumbai": {
        "Andheri East": 1.0,
        "Bandra West": 0.32,
        "Kurla": 0.48,
        "Lower Parel": 0.41,
        "Powai": 0.22,
    },
    "Bengaluru": {
        "Whitefield": 0.4,
        "Indiranagar": 0.26,
        "Koramangala": 0.28,
        "Electronic City": 0.35,
        "Hebbal": 0.3,
    },
    "Delhi": {
        "Dwarka": 0.31,
        "Saket": 0.23,
        "Rohini": 0.37,
        "Karol Bagh": 0.29,
        "Laxmi Nagar": 0.34,
    },
}

TRIGGER_CONFIG: dict[str, dict[str, Any]] = {
    "rainfall": {
        "label": "Heavy rainfall",
        "severity": 0.53,
        "threshold": "20mm/hr sustained for 2 hours",
        "tone": "storm",
    },
    "AQI": {
        "label": "Severe AQI spike",
        "severity": 0.42,
        "threshold": "AQI breached 400 for 90 minutes",
        "tone": "air",
    },
    "flood_alert": {
        "label": "Flood alert",
        "severity": 0.61,
        "threshold": "City flood warning active in worker zone",
        "tone": "alert",
    },
}


DEFAULT_WORKERS: dict[str, dict[str, Any]] = {
    "arjun": {
        "id": "arjun",
        "name": "Arjun Sharma",
        "phone_number": "+91 98765 43210",
        "preferred_language": "Hindi",
        "city": "Mumbai",
        "zone": "Andheri East",
        "platform": "Swiggy",
        "hours_per_day": 9,
        "average_daily_income": 780,
        "zone_risk": 1.0,
        "recent_activity_minutes": 14,
        "zone_match": True,
        "device_integrity": True,
        "on_shift": True,
        "tier": "Rakshak",
        "policy_active": True,
        "valid_until": utc_now() + timedelta(days=6),
        "phone_verified": True,
        "aadhaar_last4": "4421",
        "payout_upi": "arjun@okaxis",
        "emergency_contact": "Neha Sharma · +91 98200 10001",
        "auto_renew": True,
        "onboarding_completed": True,
        "joined_at": utc_now() - timedelta(days=78),
    },
    "rahul": {
        "id": "rahul",
        "name": "Rahul Shaikh",
        "phone_number": "+91 91234 56780",
        "preferred_language": "Hindi",
        "city": "Mumbai",
        "zone": "Bandra West",
        "platform": "Zomato",
        "hours_per_day": 5,
        "average_daily_income": 620,
        "zone_risk": 0.05,
        "recent_activity_minutes": 27,
        "zone_match": True,
        "device_integrity": True,
        "on_shift": True,
        "tier": "Rakshak",
        "policy_active": True,
        "valid_until": utc_now() + timedelta(days=4),
        "phone_verified": True,
        "aadhaar_last4": "7713",
        "payout_upi": "rahul@ibl",
        "emergency_contact": "Sana Shaikh · +91 98190 10002",
        "auto_renew": True,
        "onboarding_completed": True,
        "joined_at": utc_now() - timedelta(days=55),
    },
    "imran": {
        "id": "imran",
        "name": "Imran Khan",
        "phone_number": "+91 99870 34567",
        "preferred_language": "English",
        "city": "Mumbai",
        "zone": "Kurla",
        "platform": "Zepto",
        "hours_per_day": 7,
        "average_daily_income": 690,
        "zone_risk": 0.48,
        "recent_activity_minutes": 51,
        "zone_match": False,
        "device_integrity": True,
        "on_shift": True,
        "tier": "Saathi",
        "policy_active": False,
        "valid_until": None,
        "phone_verified": True,
        "aadhaar_last4": "1840",
        "payout_upi": "imran@oksbi",
        "emergency_contact": "Aamir Khan · +91 98700 10003",
        "auto_renew": False,
        "onboarding_completed": True,
        "joined_at": utc_now() - timedelta(days=34),
    },
}


class SendOtpRequest(BaseModel):
    phone_number: str


class VerifyOtpRequest(BaseModel):
    worker_id: str
    otp_code: str


class PolicyPurchaseRequest(BaseModel):
    worker_id: str
    tier: str


class TriggerSimulationRequest(BaseModel):
    worker_id: str
    trigger_type: str


class WorkerUpdateRequest(BaseModel):
    name: str | None = None
    city: str | None = None
    preferred_language: str | None = None
    zone: str | None = None
    platform: str | None = None
    hours_per_day: int | None = None
    average_daily_income: int | None = None
    payout_upi: str | None = None
    emergency_contact: str | None = None
    aadhaar_last4: str | None = None
    auto_renew: bool | None = None
    onboarding_completed: bool | None = None


workers = deepcopy(DEFAULT_WORKERS)
claims_by_worker: dict[str, dict[str, Any]] = {}
claims_by_id: dict[str, dict[str, Any]] = {}
metrics = {
    "triggers_fired": 0,
    "claims_initiated": 0,
    "payouts_credited": 0,
    "trigger_counts": Counter(),
}


def mask_phone_number(phone_number: str) -> str:
    digits = "".join(char for char in phone_number if char.isdigit())
    if len(digits) < 4:
        return phone_number
    return f"+91 •••••• {digits[-4:]}"


def default_zone_for_city(city: str) -> str:
    zones = CITY_ZONE_RISK.get(city) or CITY_ZONE_RISK["Mumbai"]
    return next(iter(zones))


def resolve_zone_risk(city: str, zone: str) -> float:
    return CITY_ZONE_RISK.get(city, {}).get(zone, 0.35)


def recommended_tier(worker: dict[str, Any]) -> str:
    if worker["zone_risk"] >= 0.75 or worker["hours_per_day"] >= 9:
        return "Suraksha"
    if worker["zone_risk"] >= 0.35 or worker["hours_per_day"] >= 6:
        return "Rakshak"
    return "Saathi"


def profile_completion(worker: dict[str, Any]) -> int:
    required_fields = [
        worker.get("phone_verified"),
        worker.get("name"),
        worker.get("city"),
        worker.get("preferred_language"),
        worker.get("zone"),
        worker.get("platform"),
        worker.get("hours_per_day"),
        worker.get("average_daily_income"),
        worker.get("payout_upi"),
        worker.get("aadhaar_last4"),
    ]
    completed = sum(1 for item in required_fields if item)
    return int(round((completed / len(required_fields)) * 100))


def recompute_worker_state(worker: dict[str, Any]) -> None:
    worker["zone"] = worker.get("zone") or default_zone_for_city(worker["city"])
    worker["zone_risk"] = resolve_zone_risk(worker["city"], worker["zone"])
    worker["hours_per_day"] = worker.get("hours_per_day") or 6
    worker["average_daily_income"] = worker.get("average_daily_income") or 650
    worker["tier"] = worker.get("tier") or recommended_tier(worker)
    requirements_met = bool(
        worker.get("phone_verified")
        and worker.get("name")
        and worker.get("city")
        and worker.get("preferred_language")
        and worker.get("zone")
        and worker.get("platform")
        and worker.get("hours_per_day")
        and worker.get("average_daily_income")
        and worker.get("payout_upi")
        and worker.get("aadhaar_last4")
    )
    worker["onboarding_completed"] = bool(worker.get("onboarding_completed") and requirements_met)


for seeded_worker in workers.values():
    recompute_worker_state(seeded_worker)


def calculate_premium(worker: dict[str, Any], tier: str) -> int:
    config = TIER_CONFIG[tier]
    price = round(
        config["base_premium"] * (0.78 + worker["zone_risk"] * 0.4)
        + max(worker["hours_per_day"] - 4, 0) * 2
    )
    return max(config["base_premium"], price)


def payout_amount(worker: dict[str, Any], tier: str, trigger_type: str) -> int:
    tier_config = TIER_CONFIG[tier]
    amount = tier_config["max_payout"] * TRIGGER_CONFIG[trigger_type]["severity"]
    amount += max(worker["hours_per_day"] - 6, 0) * 12
    return int(round(amount / 10.0) * 10)


def fraud_score(worker: dict[str, Any]) -> int:
    score = 42
    score += 18 if worker["on_shift"] else -20
    score += 16 if worker["zone_match"] else -18
    score += 12 if worker["device_integrity"] else -24
    score += max(0, 24 - worker["recent_activity_minutes"]) // 2
    return max(22, min(score, 98))


def claim_status_from_score(score: int) -> str:
    if score >= 80:
        return "Green"
    if score >= 55:
        return "Amber"
    return "Red"


def worker_response(worker: dict[str, Any]) -> dict[str, Any]:
    recommended = recommended_tier(worker)
    return {
        "id": worker["id"],
        "name": worker["name"],
        "phone_number": worker.get("phone_number"),
        "masked_phone_number": mask_phone_number(worker.get("phone_number", "")),
        "preferred_language": worker.get("preferred_language"),
        "city": worker["city"],
        "zone": worker["zone"],
        "platform": worker["platform"],
        "hours_per_day": worker["hours_per_day"],
        "average_daily_income": worker["average_daily_income"],
        "tier": worker["tier"],
        "recommended_tier": recommended,
        "premium_amount": calculate_premium(worker, worker["tier"]),
        "policy_active": worker["policy_active"],
        "valid_until": isoformat(worker["valid_until"]),
        "phone_verified": worker.get("phone_verified", False),
        "aadhaar_verified": bool(worker.get("aadhaar_last4")),
        "payout_upi": worker.get("payout_upi"),
        "emergency_contact": worker.get("emergency_contact"),
        "auto_renew": worker.get("auto_renew", False),
        "onboarding_completed": worker.get("onboarding_completed", False),
        "profile_completion": profile_completion(worker),
        "joined_at": isoformat(worker.get("joined_at")),
    }


def admin_worker_response(worker: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": worker["id"],
        "name": worker["name"],
        "city": worker["city"],
        "zone": worker["zone"],
        "platform": worker["platform"],
        "tier": worker["tier"],
        "recommended_tier": recommended_tier(worker),
        "premium_amount": calculate_premium(worker, worker["tier"]),
        "policy_active": worker["policy_active"],
        "valid_until": isoformat(worker["valid_until"]),
        "onboarding_completed": worker["onboarding_completed"],
        "profile_completion": profile_completion(worker),
        "average_daily_income": worker["average_daily_income"],
        "hours_per_day": worker["hours_per_day"],
        "zone_risk": worker["zone_risk"],
        "recent_activity_minutes": worker["recent_activity_minutes"],
        "fraud_score": fraud_score(worker),
    }


def claim_response(claim: dict[str, Any]) -> dict[str, Any]:
    return {
        "claim_id": claim["claim_id"],
        "worker_id": claim["worker_id"],
        "trigger_type": claim["trigger_type"],
        "status": claim["status"],
        "payout_amount": claim["payout_amount"],
        "payout_status": claim["payout_status"],
        "fraud_score": claim["fraud_score"],
        "trigger_label": claim["trigger_label"],
        "threshold_crossed": claim["threshold_crossed"],
        "triggered_at": isoformat(claim["triggered_at"]),
        "payout_at": isoformat(claim["payout_at"]),
    }


def create_claim(worker: dict[str, Any], trigger_type: str, occurred_at: datetime | None = None) -> dict[str, Any]:
    trigger = TRIGGER_CONFIG[trigger_type]
    score = fraud_score(worker)
    event_time = occurred_at or utc_now()
    claim_id = f"clm_{uuid4().hex[:8]}"
    claim = {
        "claim_id": claim_id,
        "worker_id": worker["id"],
        "trigger_type": trigger_type,
        "trigger_label": trigger["label"],
        "threshold_crossed": trigger["threshold"],
        "status": f"{claim_status_from_score(score)} - Auto approved",
        "payout_amount": payout_amount(worker, worker["tier"], trigger_type),
        "payout_status": "Credited",
        "fraud_score": score,
        "triggered_at": event_time,
        "payout_at": event_time + timedelta(minutes=2),
    }
    claims_by_worker[worker["id"]] = claim
    claims_by_id[claim_id] = claim
    metrics["claims_initiated"] += 1
    metrics["payouts_credited"] += 1
    return claim


def build_notification(claim: dict[str, Any], worker: dict[str, Any]) -> tuple[str, str, str]:
    english = (
        f"{worker['name'].split()[0]}, GigShield detected {claim['trigger_label'].lower()} in "
        f"{worker['zone']}. Your payout of ₹{claim['payout_amount']} has been credited under "
        f"your {worker['tier']} weekly cover."
    )
    hindi = (
        f"{worker['name'].split()[0]} bhai, {worker['zone']} mein {claim['trigger_label'].lower()} "
        f"detect hua. Aapka ₹{claim['payout_amount']} payout {worker['tier']} plan ke tahat credit ho gaya hai."
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return hindi, english, "fallback"

    try:
        client = OpenAI(api_key=api_key)
        completion = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Generate a short WhatsApp-style payout notification for an Indian food delivery worker. "
                        "Return Hindi on the first line and English on the second line. Keep both lines empathetic "
                        "and under 30 words each."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Worker: {worker['name']}. Zone: {worker['zone']}. Trigger: {claim['trigger_label']}. "
                        f"Payout amount: ₹{claim['payout_amount']}. Tier: {worker['tier']}."
                    ),
                },
            ],
        )
        text = completion.output_text.strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) >= 2:
            return lines[0], lines[1], "openai"
    except Exception:
        pass

    return hindi, english, "fallback"


def seed_demo_activity() -> None:
    demo_events = [
        ("arjun", "rainfall", utc_now() - timedelta(minutes=18)),
        ("rahul", "AQI", utc_now() - timedelta(hours=2, minutes=12)),
    ]
    for worker_id, trigger_type, occurred_at in demo_events:
        worker = workers[worker_id]
        metrics["triggers_fired"] += 1
        metrics["trigger_counts"][trigger_type] += 1
        create_claim(worker, trigger_type, occurred_at)


seed_demo_activity()


app = FastAPI(title="GigShield API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="assets")


def get_worker_or_404(worker_id: str) -> dict[str, Any]:
    worker = workers.get(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@app.get("/", response_model=None)
def root():
    if FRONTEND_INDEX_FILE.exists():
        return FileResponse(FRONTEND_INDEX_FILE)
    return {"product": "GigShield", "status": "ready"}


@app.get("/favicon.svg")
def favicon() -> FileResponse:
    file_path = FRONTEND_DIST_DIR / "favicon.svg"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Frontend asset not found")
    return FileResponse(file_path)


@app.get("/icons.svg")
def icons() -> FileResponse:
    file_path = FRONTEND_DIST_DIR / "icons.svg"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Frontend asset not found")
    return FileResponse(file_path)


@app.post("/auth/send-otp")
def send_otp(payload: SendOtpRequest) -> dict[str, Any]:
    worker = next(
        (item for item in workers.values() if item.get("phone_number") == payload.phone_number),
        None,
    )

    if worker is None:
        city = "Mumbai"
        zone = default_zone_for_city(city)
        worker_id = f"wrk_{uuid4().hex[:8]}"
        worker = {
            "id": worker_id,
            "name": "",
            "phone_number": payload.phone_number,
            "preferred_language": "English",
            "city": city,
            "zone": zone,
            "platform": "",
            "hours_per_day": 6,
            "average_daily_income": 650,
            "zone_risk": resolve_zone_risk(city, zone),
            "recent_activity_minutes": 18,
            "zone_match": True,
            "device_integrity": True,
            "on_shift": True,
            "tier": "Rakshak",
            "policy_active": False,
            "valid_until": None,
            "phone_verified": False,
            "aadhaar_last4": "",
            "payout_upi": "",
            "emergency_contact": "",
            "auto_renew": True,
            "onboarding_completed": False,
            "joined_at": utc_now(),
        }
        workers[worker_id] = worker

    recompute_worker_state(worker)

    return {
        "worker_id": worker["id"],
        "masked_phone_number": mask_phone_number(payload.phone_number),
        "otp_code": "121212",
        "expires_in_seconds": 300,
        "existing_account": worker["onboarding_completed"],
    }


@app.post("/auth/verify-otp")
def verify_otp(payload: VerifyOtpRequest) -> dict[str, Any]:
    worker = get_worker_or_404(payload.worker_id)
    if payload.otp_code != "121212":
        raise HTTPException(status_code=400, detail="Invalid verification code")

    worker["phone_verified"] = True
    recompute_worker_state(worker)
    return {"verified": True, "worker": worker_response(worker)}


@app.get("/worker/{worker_id}")
def get_worker(worker_id: str) -> dict[str, Any]:
    worker = get_worker_or_404(worker_id)
    return worker_response(worker)


@app.patch("/worker/{worker_id}")
def update_worker(worker_id: str, payload: WorkerUpdateRequest) -> dict[str, Any]:
    worker = get_worker_or_404(worker_id)
    updates = payload.model_dump(exclude_none=True)

    if "aadhaar_last4" in updates and len(updates["aadhaar_last4"]) != 4:
        raise HTTPException(status_code=400, detail="Aadhaar must be the last 4 digits")

    if "hours_per_day" in updates and updates["hours_per_day"] <= 0:
        raise HTTPException(status_code=400, detail="Working hours must be positive")

    if "average_daily_income" in updates and updates["average_daily_income"] <= 0:
        raise HTTPException(status_code=400, detail="Average daily income must be positive")

    worker.update(updates)
    recompute_worker_state(worker)
    return worker_response(worker)


@app.post("/policy/buy")
def buy_policy(payload: PolicyPurchaseRequest) -> dict[str, Any]:
    worker = get_worker_or_404(payload.worker_id)
    if payload.tier not in TIER_CONFIG:
        raise HTTPException(status_code=400, detail="Unknown tier")
    if not worker["phone_verified"] or not worker["onboarding_completed"]:
        raise HTTPException(status_code=400, detail="Complete onboarding before activating cover")

    worker["tier"] = payload.tier
    worker["policy_active"] = True
    worker["valid_until"] = utc_now() + timedelta(days=7)
    premium = calculate_premium(worker, payload.tier)

    return {
        "policy_id": f"pol_{worker['id']}_{uuid4().hex[:8]}",
        "tier": payload.tier,
        "premium_amount": premium,
        "valid_until": isoformat(worker["valid_until"]),
        "policy_active": True,
    }


@app.post("/trigger/simulate")
def simulate_trigger(payload: TriggerSimulationRequest) -> dict[str, Any]:
    worker = workers.get(payload.worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    if payload.trigger_type not in TRIGGER_CONFIG:
        raise HTTPException(status_code=400, detail="Unknown trigger")

    metrics["triggers_fired"] += 1
    metrics["trigger_counts"][payload.trigger_type] += 1

    trigger = TRIGGER_CONFIG[payload.trigger_type]
    score = fraud_score(worker)

    if not worker["policy_active"]:
        return {
            "trigger_type": payload.trigger_type,
            "threshold_crossed": trigger["threshold"],
            "claim_id": None,
            "claims_initiated": False,
            "payout_amount": 0,
            "fraud_score": score,
            "reason": "Weekly cover is inactive",
        }

    claim = create_claim(worker, payload.trigger_type)

    return {
        "trigger_type": payload.trigger_type,
        "threshold_crossed": trigger["threshold"],
        "claim_id": claim["claim_id"],
        "claims_initiated": True,
        "payout_amount": claim["payout_amount"],
        "fraud_score": score,
    }


@app.get("/claim/{worker_id}")
def get_claim(worker_id: str) -> dict[str, Any]:
    claim = claims_by_worker.get(worker_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found for worker")
    return claim_response(claim)


@app.get("/notify/{claim_id}")
def get_notification(claim_id: str) -> dict[str, Any]:
    claim = claims_by_id.get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    worker = workers[claim["worker_id"]]
    hindi, english, source = build_notification(claim, worker)
    return {
        "message_hindi": hindi,
        "message_english": english,
        "timestamp": isoformat(utc_now()),
        "source": source,
    }


@app.get("/admin/workers")
def admin_workers() -> dict[str, Any]:
    ordered_workers = sorted(
        workers.values(),
        key=lambda worker: (not worker["policy_active"], worker["zone_risk"] * -1, worker["name"]),
    )
    return {
        "workers": [admin_worker_response(worker) for worker in ordered_workers],
        "triggers": [
            {
                "id": trigger_id,
                "label": config["label"],
                "threshold": config["threshold"],
            }
            for trigger_id, config in TRIGGER_CONFIG.items()
        ],
    }


@app.get("/admin/summary")
def admin_summary() -> dict[str, Any]:
    recent_claims = [
        {
            "claim_id": claim["claim_id"],
            "worker_name": workers[claim["worker_id"]]["name"],
            "zone": workers[claim["worker_id"]]["zone"],
            "trigger_type": claim["trigger_type"],
            "payout_amount": claim["payout_amount"],
            "fraud_score": claim["fraud_score"],
            "payout_status": claim["payout_status"],
        }
        for claim in sorted(
            claims_by_id.values(),
            key=lambda item: item["triggered_at"],
            reverse=True,
        )
    ]

    return {
        "total_workers": len(workers),
        "onboarded_workers": sum(1 for worker in workers.values() if worker["onboarding_completed"]),
        "active_policies": sum(1 for worker in workers.values() if worker["policy_active"]),
        "triggers_fired": metrics["triggers_fired"],
        "claims_initiated": metrics["claims_initiated"],
        "payouts_credited": metrics["payouts_credited"],
        "recent_claims": recent_claims[:5],
        "trigger_counts": dict(metrics["trigger_counts"]),
    }


@app.get("/{full_path:path}", response_model=None)
def frontend_routes(full_path: str):
    if not FRONTEND_INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="Frontend build not found")
    return FileResponse(FRONTEND_INDEX_FILE)

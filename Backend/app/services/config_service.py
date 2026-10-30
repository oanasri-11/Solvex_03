"""System Config, Localized Content & Guidelines service (Section 15)."""

from typing import Dict, Any


def get_patient_content(lang: str = "fr") -> Dict[str, Any]:
    """Emergency guidance texts, emergency phone numbers, and red-flag symptom screen in FR/AR."""
    if lang.lower().startswith("ar"):
        return {
            "emergency_numbers": {
                "protection_civile": "14",
                "samu": "1021",
                "general_emergency": "112",
            },
            "emergency_guidance": (
                "إذا كانت قراءتك أعلى من 180/110 ملم زئبق ولديك أعراض مقلقة "
                "(ألم في الصدر، صعوبة في التنفس، صداع حاد، تشوش في الرؤية، ضعف مفاجئ)، "
                "يرجى الاتصال فوراً بالإسعاف (14 أو 1021) أو التوجه لأقرب قسم طوارئ."
            ),
            "urgent_repeat_guidance": (
                "إذا كانت قراءتك مرتفعة جداً بدون أعراض، استرح لمدة 5 دقائق وأعد القياس. "
                "إذا ظلت مرتفعة، اتصل بطبيبك أو اطلب المساعدة فوراً."
            ),
            "red_flag_symptoms": [
                {"code": "chest_pain", "label": "ألم أو ضغط في الصدر"},
                {"code": "shortness_of_breath", "label": "صعوبة أو ضيق في التنفس"},
                {"code": "severe_headache", "label": "صداع حاد ومفاجئ"},
                {"code": "blurred_vision", "label": "تشوش في الرؤية"},
                {"code": "numbness_weakness", "label": "ضعف أو خدر في الوجه أو الذراع أو الساق"},
                {"code": "difficulty_speaking", "label": "صعوبة في الكلام أو النطق"},
            ],
            "language": "ar-DZ",
        }

    # Default to French (Algerian context)
    return {
        "emergency_numbers": {
            "protection_civile": "14",
            "samu": "1021",
            "general_emergency": "112",
        },
        "emergency_guidance": (
            "Si votre tension dépasse 180/110 mmHg et que vous présentez des symptômes "
            "(douleur thoracique, essoufflement, maux de tête violents, troubles visuels, faiblesse soudaine), "
            "contactez immédiatement les secours (Protection Civile : 14 ou SAMU : 1021) ou rendez-vous aux urgences."
        ),
        "urgent_repeat_guidance": (
            "Si votre tension est très élevée sans symptômes, reposez-vous pendant 5 minutes et reprenez la mesure. "
            "Si la tension reste élevée, contactez votre médecin ou envoyez une demande d'aide."
        ),
        "red_flag_symptoms": [
            {"code": "chest_pain", "label": "Douleur ou serrement dans la poitrine"},
            {"code": "shortness_of_breath", "label": "Difficulté respiratoire ou essoufflement"},
            {"code": "severe_headache", "label": "Maux de tête intenses et inhabituels"},
            {"code": "blurred_vision", "label": "Troubles de la vue (flou, taches)"},
            {"code": "numbness_weakness", "label": "Engourdissement ou paralysie d'un côté du corps"},
            {"code": "difficulty_speaking", "label": "Difficulté à parler ou articuler"},
        ],
        "language": "fr-DZ",
    }


def get_labels(lang: str = "fr") -> Dict[str, Any]:
    """Status labels, alert tier names, data-quality warning strings, priority reason codes."""
    if lang.lower().startswith("ar"):
        return {
            "status_levels": {
                "normal": "طبيعي",
                "elevated": "مرتفع قليلاً",
                "stage_1": "المرحلة الأولى لارتفاع الضغط",
                "stage_2": "المرحلة الثانية لارتفاع الضغط",
                "severe": "ارتفاع حاد (أزمة)",
            },
            "alert_tiers": {
                "routine_out_of_range": "خارج المعدل الطبيعي (روتيني)",
                "persistent_elevation": "ارتفاع مستمر",
                "severe_single_reading": "قراءة حادة منفردة",
                "critical_emergency": "طوارئ قصوى",
            },
            "priority_levels": {
                "P1_critical": "أولوية 1 - حرجة",
                "P2_high": "أولوية 2 - عالية",
                "P3_moderate": "أولوية 3 - متوسطة",
                "P4_routine": "أولوية 4 - روتينية",
                "not_triaged": "غير مصنف",
            },
            "data_quality_warnings": {
                "digit_preference": "تحقق: احتمال وجود تقريب في الأرقام (تفضيل الصفر)",
                "duplicate_reading": "تحقق: قراءات متطابقة في وقت متقارب",
                "late_entry": "تحقق: إدخال متأخر للبيانات مقارنة بوقت القياس",
                "device_mismatch": "تحقق: بيانات غير متوافقة مع خصائص الجهاز المسجل",
            },
            "language": "ar-DZ",
        }

    return {
        "status_levels": {
            "normal": "Normal",
            "elevated": "Élevé",
            "stage_1": "Hypertension Stade 1",
            "stage_2": "Hypertension Stade 2",
            "severe": "Hypertension Sévère",
        },
        "alert_tiers": {
            "routine_out_of_range": "Hors cible de routine",
            "persistent_elevation": "Élévation persistante",
            "severe_single_reading": "Mesure sévère isolée",
            "critical_emergency": "Urgence critique",
        },
        "priority_levels": {
            "P1_critical": "P1 - Critique",
            "P2_high": "P2 - Élevée",
            "P3_moderate": "P3 - Modérée",
            "P4_routine": "P4 - Routine",
            "not_triaged": "Non trié",
        },
        "data_quality_warnings": {
            "digit_preference": "Vérifier : suspicion d'arrondi des chiffres (biais du zéro terminal)",
            "duplicate_reading": "Vérifier : mesures identiques répétées dans un court intervalle",
            "late_entry": "Vérifier : saisie tardive par rapport à l'heure de mesure",
            "device_mismatch": "Vérifier : données non concordantes avec l'appareil enregistré",
        },
        "language": "fr-DZ",
    }


def get_features() -> Dict[str, bool]:
    """Operational feature flags according to specification."""
    return {
        "flag.low_bandwidth_channel": True,
        "flag.caregiver_assisted_entry": True,
        "flag.office_readings": True,
        "flag.admin_role": True,
    }

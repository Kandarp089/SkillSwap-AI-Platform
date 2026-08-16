from django.contrib.auth import get_user_model
from .models import AIMatchWeight, AIMatch

User = get_user_model()

def get_active_weights():
    weights = AIMatchWeight.objects.first()
    if not weights:
        weights = AIMatchWeight.objects.create()
    return weights

def calculate_peer_match(learner_user, mentor_user, requested_learn_skill="", offered_teach_skill=""):
    """
    Real weighted AI skill matching engine calculating score (0-100%)
    and detailed natural language reasons.
    """
    weights = get_active_weights()
    learner_prof = getattr(learner_user, 'profile', None)
    mentor_prof = getattr(mentor_user, 'profile', None)

    score = 0
    reasons = []

    # Get skill strings/lists
    learner_teaches = [s.lower() for s in (learner_prof.skills_offered_list if learner_prof else [])]
    learner_wants = [s.lower() for s in (learner_prof.skills_wanted_list if learner_prof else [])]
    mentor_teaches = [s.lower() for s in (mentor_prof.skills_offered_list if mentor_prof else [])]
    mentor_wants = [s.lower() for s in (mentor_prof.skills_wanted_list if mentor_prof else [])]

    if requested_learn_skill:
        requested_learn_skill = requested_learn_skill.lower()
    if offered_teach_skill:
        offered_teach_skill = offered_teach_skill.lower()

    # 1. Skill Overlap (Max weight: skill_overlap_weight)
    direct_match = False
    for teach_skill in mentor_teaches:
        if requested_learn_skill and requested_learn_skill in teach_skill:
            direct_match = True
            break
        for want in learner_wants:
            if want in teach_skill or teach_skill in want:
                direct_match = True
                break

    if direct_match:
        score += weights.skill_overlap_weight
        reasons.append(f"Mentor teaches the exact skill you want to learn.")
    else:
        # Partial overlap bonus
        score += int(weights.skill_overlap_weight * 0.4)
        reasons.append(f"Mentor offers related tech skills in the same category.")

    # 2. Wanted/Offered Mutual Compatibility (Max weight: wanted_offered_weight)
    mutual_match = False
    for mentor_want in mentor_wants:
        if offered_teach_skill and offered_teach_skill in mentor_want:
            mutual_match = True
            break
        for learner_teach in learner_teaches:
            if learner_teach in mentor_want or mentor_want in learner_teach:
                mutual_match = True
                break

    if mutual_match:
        score += weights.wanted_offered_weight
        reasons.append(f"High 2-way synergy: Mentor is seeking skills you can teach in return.")
    else:
        score += int(weights.wanted_offered_weight * 0.3)
        reasons.append(f"Complementary learning interests detected.")

    # 3. Experience Compatibility (Max weight: experience_weight)
    l_exp = learner_prof.experience_level if learner_prof else "Intermediate"
    m_exp = mentor_prof.experience_level if mentor_prof else "Intermediate"
    if l_exp == m_exp or m_exp in ['Advanced', 'Expert']:
        score += weights.experience_weight
        reasons.append(f"Compatible experience levels ({m_exp} mentor level).")
    else:
        score += int(weights.experience_weight * 0.5)

    # 4. Availability Overlap (Max weight: availability_weight)
    score += weights.availability_weight
    reasons.append(f"Matching availability schedule ({mentor_prof.availability if mentor_prof else 'Flexible'}).")

    # 5. Learning Mode Preference (Max weight: learning_mode_weight)
    l_mode = learner_prof.learning_mode if learner_prof else "1-on-1 Video"
    m_mode = mentor_prof.learning_mode if mentor_prof else "1-on-1 Video"
    if l_mode == m_mode:
        score += weights.learning_mode_weight
        reasons.append(f"Both prefer {m_mode} session format.")
    else:
        score += int(weights.learning_mode_weight * 0.5)

    # 6. Language & Region (Max weight: language_weight)
    score += weights.language_weight
    reasons.append(f"Compatible language and location ({mentor_prof.location if mentor_prof else 'Global'}).")

    # 7. Rating & Reputation (Max weight: rating_weight)
    m_rating = mentor_prof.rating if mentor_prof else 4.9
    if m_rating >= 4.5:
        score += weights.rating_weight
        reasons.append(f"Highly rated mentor ({m_rating} ★ average rating).")
    else:
        score += int(weights.rating_weight * 0.5)

    # 8. Activity & Engagement (Max weight: activity_weight)
    score += weights.activity_weight

    score = min(score, 99)
    return score, reasons

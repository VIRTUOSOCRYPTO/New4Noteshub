from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

# Department codes and mappings from original schema
VALID_DEPARTMENTS = [
    "NT", "EEE", "ECE", "CSE", "ISE", "AIML", "AIDS", "MECH",
    "CH", "IEM", "ETE", "MBA", "MCA", "DOS"
]

DEPARTMENT_CODES = {
    "CS": "CSE", "EC": "ECE", "IS": "ISE", "EE": "EEE",
    "ME": "MECH", "CH": "CH", "NT": "NT", "IE": "IEM",
    "ET": "ETE", "CI": "AIML", "AD": "AIDS", "MB": "MBA",
    "MC": "MCA", "DO": "DOS"
}

KARNATAKA_COLLEGES = [
    {"value": "rvce", "label": "R.V. College of Engineering, Bengaluru"},
    {"value": "msrit", "label": "M.S. Ramaiah Institute of Technology, Bengaluru"},
    {"value": "bmsce", "label": "B.M.S. College of Engineering, Bengaluru"},
    {"value": "pesu", "label": "PES University, Bengaluru"},
    {"value": "dsce", "label": "Dayananda Sagar College of Engineering, Bengaluru"},
    {"value": "nie", "label": "National Institute of Engineering, Mysuru"},
    {"value": "sit", "label": "Siddaganga Institute of Technology, Tumkuru"},
    {"value": "other", "label": "Other Institution"}
]

VALID_YEARS = [1, 2, 3, 4]

# User Models
class UserBase(BaseModel):
    usn: str
    email: EmailStr
    department: str
    college: Optional[str] = None
    year: int

    @field_validator('usn')
    @classmethod
    def validate_usn(cls, v):
        standard_format = re.compile(r'^[0-9][A-Za-z]{2}[0-9]{2}[A-Za-z]{2}[0-9]{3}$')
        short_format = re.compile(r'^[0-9]{2}[A-Za-z]{2}[0-9]{3}$')
        if not (standard_format.match(v) or short_format.match(v)):
            raise ValueError('USN must be in format 1SI20CS045 or 22EC101')
        return v.upper()

    @field_validator('department')
    @classmethod
    def validate_department(cls, v):
        if v not in VALID_DEPARTMENTS:
            raise ValueError(f'Department must be one of {VALID_DEPARTMENTS}')
        return v

    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v not in VALID_YEARS:
            raise ValueError(f'Year must be one of {VALID_YEARS}')
        return v

class UserCreate(UserBase):
    password: str
    confirmPassword: str
    customCollegeName: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    usn: str
    password: str

class UserInDB(UserBase):
    id: str
    password_hash: str
    profile_picture: Optional[str] = None
    notify_new_notes: bool = True
    notify_downloads: bool = False
    reset_token: Optional[str] = None
    reset_token_expiry: Optional[datetime] = None
    created_at: datetime
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    refresh_token: Optional[str] = None
    refresh_token_expiry: Optional[datetime] = None

class UserResponse(UserBase):
    id: str
    profile_picture: Optional[str] = None
    notify_new_notes: bool = True
    notify_downloads: bool = False
    created_at: datetime
    two_factor_enabled: bool = False

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    usn: Optional[str] = None
    user_id: Optional[str] = None

# Note Models
class NoteBase(BaseModel):
    title: str
    department: str
    year: int
    subject: str

class NoteCreate(NoteBase):
    pass

class NoteInDB(NoteBase):
    id: str
    user_id: str
    usn: str
    filename: str
    original_filename: str
    uploaded_at: datetime
    is_flagged: bool = False
    flag_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    is_approved: bool = True
    download_count: int = 0
    view_count: int = 0

class NoteResponse(NoteBase):
    id: str
    user_id: str
    usn: str
    filename: str
    original_filename: str
    uploaded_at: datetime
    is_flagged: bool = False
    is_approved: bool = True
    download_count: int = 0
    view_count: int = 0

# Search/Filter Models
class NotesSearchParams(BaseModel):
    department: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[int] = None
    userDepartment: Optional[str] = None
    userCollege: Optional[str] = None
    userYear: Optional[int] = None
    showAllDepartments: bool = False
    showAllColleges: bool = False
    showAllYears: bool = False
    userId: Optional[str] = None

# Settings Models
class UserSettingsUpdate(BaseModel):
    notify_new_notes: Optional[bool] = None
    notify_downloads: Optional[bool] = None

class PasswordUpdate(BaseModel):
    currentPassword: str
    newPassword: str
    confirmNewPassword: str

    @field_validator('newPassword')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

# Password Reset Models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str
    confirmPassword: str

# Flag/Review Models
class FlagNoteRequest(BaseModel):
    reason: str

class ReviewNoteRequest(BaseModel):
    approved: bool

# 2FA Models
class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str

class TwoFactorVerify(BaseModel):
    token: str

# Google Auth Model
class GoogleAuthRequest(BaseModel):
    idToken: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    photoURL: Optional[str] = None

# Bookmark Models
class BookmarkCreate(BaseModel):
    note_id: str

class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    note_id: str
    created_at: datetime

# Message Models
class MessageCreate(BaseModel):
    receiver_id: str
    content: str
    attachment: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    content: str
    is_read: bool
    sent_at: datetime
    attachment: Optional[str] = None

# Drawing Models
class DrawingCreate(BaseModel):
    note_id: Optional[str] = None
    title: str
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_public: bool = False

class DrawingResponse(BaseModel):
    id: str
    note_id: Optional[str] = None
    user_id: str
    title: str
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_public: bool = False

# Stats Models
class UserStats(BaseModel):
    uploadCount: int
    downloadCount: int
    viewCount: int
    daysSinceJoined: int
    previewCount: int
    uniqueSubjectsCount: int
    pagesVisited: int

# Gamification Models
class StreakData(BaseModel):
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    total_activities: int = 0

class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    days_until_next_milestone: int
    next_milestone: int

class UserPoints(BaseModel):
    user_id: str
    total_points: int = 0
    level: int = 1
    points_to_next_level: int = 100

class PointsResponse(BaseModel):
    total_points: int
    level: int
    level_name: str
    points_to_next_level: int
    progress_percentage: float

class PointsHistoryItem(BaseModel):
    action: str
    points: int
    timestamp: datetime

# Referral Models
class ReferralData(BaseModel):
    user_id: str
    referral_code: str
    referred_by: Optional[str] = None
    referred_users: List[str] = []
    total_referrals: int = 0
    rewards_earned: dict = {
        "bonus_downloads": 0,
        "ai_access_days": 0,
        "premium_days": 0
    }

class ReferralResponse(BaseModel):
    referral_code: str
    total_referrals: int
    rewards_earned: dict
    referral_link: str

class ReferralReward(BaseModel):
    type: str  # "signup", "first_upload"
    bonus_downloads: int = 0
    ai_access_days: int = 0

# Leaderboard Models
class LeaderboardEntry(BaseModel):
    user_id: str
    usn: str
    rank: int
    score: int
    college: Optional[str] = None
    department: str
    profile_picture: Optional[str] = None
    streak: int = 0
    level: int = 1

class LeaderboardResponse(BaseModel):
    type: str  # "college", "department", "all_india"
    filter: Optional[dict] = None
    rankings: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_users: int
    updated_at: datetime

class LeaderboardQuery(BaseModel):
    type: str  # "college", "department", "all_india"
    college: Optional[str] = None
    department: Optional[str] = None
    limit: int = 100

# Social Sharing Models
class ShareAction(BaseModel):
    note_id: str
    platform: str  # "whatsapp", "instagram", "twitter", "facebook"

class ShareStats(BaseModel):
    total_shares: int
    platform_breakdown: dict
    most_shared_note: Optional[str] = None

# Achievement Models
class AchievementDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: str  # "upload", "download", "social", "hidden", "rare"
    icon: str  # emoji or icon name
    criteria: dict  # e.g., {"uploads": 1}, {"downloads": 100}
    rarity: str  # "common", "uncommon", "rare", "epic", "legendary"
    points: int  # bonus points awarded

class UserAchievement(BaseModel):
    user_id: str
    achievement_id: str
    unlocked_at: datetime
    progress: Optional[dict] = None

class AchievementResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    icon: str
    rarity: str
    points: int
    unlocked: bool
    unlocked_at: Optional[datetime] = None
    progress: Optional[dict] = None

class AchievementProgress(BaseModel):
    achievement_id: str
    current: int
    required: int
    percentage: float

# Study Group Models
class StudyGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    is_private: bool = False
    max_members: int = 50

class StudyGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    is_private: Optional[bool] = None

class StudyGroupMember(BaseModel):
    user_id: str
    usn: str
    role: str  # "admin", "moderator", "member"
    joined_at: datetime

class StudyGroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    created_by: str
    created_at: datetime
    is_private: bool
    member_count: int
    members: List[StudyGroupMember]
    max_members: int

class GroupChatMessage(BaseModel):
    group_id: str
    user_id: str
    usn: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GroupChatMessageResponse(BaseModel):
    id: str
    group_id: str
    user_id: str
    usn: str
    message: str
    timestamp: datetime

class GroupTask(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

class GroupTaskResponse(BaseModel):
    id: str
    group_id: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    created_by: str
    created_at: datetime
    completed: bool

# Follow System Models
class FollowAction(BaseModel):
    following_id: str  # user being followed

class FollowResponse(BaseModel):
    user_id: str
    following_id: str
    followed_at: datetime

class FollowStats(BaseModel):
    followers_count: int
    following_count: int
    is_following: bool

class ActivityFeedItem(BaseModel):
    user_id: str
    usn: str
    activity_type: str  # "upload", "achievement", "level_up", "streak"
    details: dict
    timestamp: datetime
    profile_picture: Optional[str] = None

class ActivityFeedResponse(BaseModel):
    activities: List[ActivityFeedItem]
    has_more: bool

# Exam Schedule Models
class ExamCreate(BaseModel):
    subject: str
    department: str
    year: int
    exam_date: datetime
    exam_type: str  # "midterm", "final", "quiz"

class ExamResponse(BaseModel):
    id: str
    subject: str
    department: str
    year: int
    exam_date: datetime
    exam_type: str
    days_until: int
    created_at: datetime

class ExamCountdown(BaseModel):
    next_exam: Optional[ExamResponse] = None
    upcoming_exams: List[ExamResponse]
    trending_notes: List[str] = []

# Month 2: Challenges & Competitions Models
class ChallengeCreate(BaseModel):
    challenge_type: str
    target: int
    reward_points: int

class ChallengeResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    target: int
    current_progress: int
    completed: bool
    reward_points: int
    date: str

class BattleCreate(BaseModel):
    opponent_id: str
    challenge_type: str
    duration_days: int = 7

class BattleResponse(BaseModel):
    id: str
    challenger_id: str
    opponent_id: str
    challenge_type: str
    status: str
    challenger_score: int
    opponent_score: int
    end_date: datetime

# Month 2: Contests Models
class ContestCreate(BaseModel):
    title: str
    description: str
    category: str
    duration_days: int = 30

class ContestResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    start_date: datetime
    end_date: datetime
    status: str
    entry_count: Optional[int] = 0

class ContestEntryCreate(BaseModel):
    contest_id: str
    note_id: str
    description: Optional[str] = None

# Month 2: FOMO & Rewards (no additional models needed - using dynamic responses)

# Month 2: WhatsApp Share Models
class WhatsAppShareRequest(BaseModel):
    share_type: str
    item_id: Optional[str] = None

class WhatsAppShareResponse(BaseModel):
    whatsapp_link: str
    qr_code: Optional[str] = None
    message_preview: str

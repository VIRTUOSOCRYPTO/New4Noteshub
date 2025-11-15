import { z } from "zod";

// Shared schema types for frontend
export const VALID_DEPARTMENTS = [
  "NT", "EEE", "ECE", "CSE", "ISE", "AIML", "AIDS", "MECH",
  "CH", "IEM", "ETE", "MBA", "MCA", "DOS"
];

export const DEPARTMENT_CODES: Record<string, string> = {
  "CS": "CSE", "EC": "ECE", "IS": "ISE", "EE": "EEE",
  "ME": "MECH", "CH": "CH", "NT": "NT", "IE": "IEM",
  "ET": "ETE", "CI": "AIML", "AD": "AIDS", "MB": "MBA",
  "MC": "MCA", "DO": "DOS"
};

export const KARNATAKA_COLLEGES = [
  { value: "rvce", label: "R.V. College of Engineering, Bengaluru" },
  { value: "msrit", label: "M.S. Ramaiah Institute of Technology, Bengaluru" },
  { value: "bmsce", label: "B.M.S. College of Engineering, Bengaluru" },
  { value: "pesu", label: "PES University, Bengaluru" },
  { value: "dsce", label: "Dayananda Sagar College of Engineering, Bengaluru" },
  { value: "nie", label: "National Institute of Engineering, Mysuru" },
  { value: "sit", label: "Siddaganga Institute of Technology, Tumkuru" },
  { value: "ait", label: "Acharya Institute of Technology, Bengaluru" },
  { value: "jssate", label: "JSS Academy of Technical Education, Bengaluru" },
  { value: "sjbit", label: "SJB Institute of Technology, Bengaluru" },
  { value: "sjce", label: "Sri Jayachamarajendra College of Engineering, Mysuru" },
  { value: "nmit", label: "Nitte Meenakshi Institute of Technology, Bengaluru" },
  { value: "biet", label: "Bapuji Institute of Engineering and Technology, Davangere" },
  { value: "cmrit", label: "CMR Institute of Technology, Bengaluru" },
  { value: "rnsit", label: "RNS Institute of Technology, Bengaluru" },
  { value: "other", label: "Other Institution" }
];

export const VALID_YEARS = [1, 2, 3, 4];

export const SEMESTERS_BY_YEAR: Record<number, number[]> = {
  1: [1, 2],
  2: [3, 4],
  3: [5, 6],
  4: [7, 8]
};

// User types
export interface User {
  id: string;
  usn: string;
  email: string;
  department: string;
  college?: string;
  year: number;
  profile_picture?: string;
  notify_new_notes: boolean;
  notify_downloads: boolean;
  created_at: string;
  two_factor_enabled: boolean;
}

export interface RegisterUser {
  usn: string;
  email: string;
  department: string;
  college: string;
  year: number;
  password: string;
  confirmPassword: string;
  customCollegeName?: string;
}

export interface LoginUser {
  usn: string;
  password: string;
}

// Note types
export interface Note {
  id: string;
  userId: string;
  usn: string;
  title: string;
  department: string;
  year: number;
  subject: string;
  filename: string;
  originalFilename: string;
  uploadedAt: string;
  isFlagged: boolean;
  isApproved?: boolean;
  downloadCount: number;
  viewCount: number;
  flagReason?: string;
}

export interface SearchNotesParams {
  department?: string;
  subject?: string;
  year?: number;
  userDepartment?: string;
  userCollege?: string;
  userYear?: number;
  showAllDepartments?: boolean;
  showAllColleges?: boolean;
  showAllYears?: boolean;
  userId?: string;
}

// Settings types
export interface UpdateUserSettings {
  notify_new_notes?: boolean;
  notify_downloads?: boolean;
}

export interface UpdatePassword {
  currentPassword: string;
  newPassword: string;
  confirmNewPassword: string;
}

// Password reset types
export interface ForgotPassword {
  email: string;
}

export interface ResetPassword {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

// Stats types
export interface UserStats {
  uploadCount: number;
  downloadCount: number;
  viewCount: number;
  daysSinceJoined: number;
  previewCount: number;
  uniqueSubjectsCount: number;
  pagesVisited: number;
}

// Zod validation schemas
export const loginUserSchema = z.object({
  usn: z.string()
    .refine(
      (value) => {
        const standardFormat = /^[0-9][A-Za-z]{2}[0-9]{2}[A-Za-z]{2}[0-9]{3}$/;
        const shortFormat = /^[0-9]{2}[A-Za-z]{2}[0-9]{3}$/;
        return standardFormat.test(value) || shortFormat.test(value);
      },
      {
        message: "USN must be in format 1SI20CS045 or 22EC101"
      }
    ),
  password: z.string().min(1, "Password is required"),
});

export const registerUserSchema = z.object({
  usn: z.string()
    .refine(
      (value) => {
        const standardFormat = /^[0-9][A-Za-z]{2}[0-9]{2}[A-Za-z]{2}[0-9]{3}$/;
        const shortFormat = /^[0-9]{2}[A-Za-z]{2}[0-9]{3}$/;
        return standardFormat.test(value) || shortFormat.test(value);
      },
      {
        message: "USN must be in format 1SI20CS045 or 22EC101"
      }
    ),
  email: z.string().email("Please enter a valid email address").min(1, "Email is required"),
  department: z.enum(VALID_DEPARTMENTS as [string, ...string[]], {
    errorMap: () => ({ message: "Please select a valid department" })
  }),
  college: z.string().min(1, "Please select your college"),
  year: z.number({
    required_error: "Please select your academic year",
    invalid_type_error: "Year must be a number"
  }).min(1, "Please select your academic year").max(4, "Invalid year selected"),
  customCollegeName: z.string().optional(),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[^A-Za-z0-9]/, "Password must contain at least one special character"),
  confirmPassword: z.string().min(8, "Password must be at least 8 characters"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

export const forgotPasswordSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

export const resetPasswordSchema = z.object({
  token: z.string().min(1, "Reset token is required"),
  newPassword: z.string()
    .min(8, "New password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[^A-Za-z0-9]/, "Password must contain at least one special character"),
  confirmPassword: z.string().min(8, "Password confirmation must be at least 8 characters"),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

// College codes mapping
export const COLLEGE_CODES: Record<string, string> = {
  "RV": "rvce",
  "MS": "msrit",
  "BM": "bmsce",
  "PE": "pesu",
  "DS": "dsce",
  "NI": "nie",
  "SI": "sit",
  "AC": "ait",
  "JS": "jssate",
  "SJ": "sjbit",
  "SC": "sjce",
  "NM": "nmit",
  "BI": "biet",
  "CM": "cmrit",
  "RN": "rnsit",
};

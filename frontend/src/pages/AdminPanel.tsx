import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { apiRequest } from "@/lib/api";
import { showToast } from "@/components/ui/toast-container";
import { Button } from "@/components/ui/button";
import {
  Users,
  Search,
  Filter,
  Download,
  Edit,
  Trash2,
  RefreshCw,
  BarChart3,
  Shield,
  X,
  MessageSquare
} from "lucide-react";
import FeedbackManagement from "@/components/admin/FeedbackManagement";

interface User {
  id: string;
  usn: string;
  email: string;
  department: string;
  college: string;
  year: number;
  createdAt: string;
  notes_count?: number;
  points?: number;
  level?: number;
}

interface UserStats {
  total_users: number;
  by_department: Array<{ _id: string; count: number }>;
  by_college: Array<{ _id: string; count: number }>;
  by_year: Array<{ _id: number; count: number }>;
  recent_signups_7d: number;
}

export default function AdminPanel() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDept, setFilterDept] = useState("");
  const [filterCollege, setFilterCollege] = useState("");
  const [filterYear, setFilterYear] = useState("");
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [hasAdminAccess, setHasAdminAccess] = useState(false);
  const [checkingAdmin, setCheckingAdmin] = useState(true);
  const [activeTab, setActiveTab] = useState<'users' | 'feedback'>('users');

  // Check admin access from API
  useEffect(() => {
    const checkAdminStatus = async () => {
      if (!user) {
        setCheckingAdmin(false);
        return;
      }
      
      try {
        const data = await apiRequest("/api/user/is-admin");
        setHasAdminAccess(data.is_admin || false);
      } catch (error) {
        console.error("Failed to check admin status:", error);
        setHasAdminAccess(false);
      } finally {
        setCheckingAdmin(false);
      }
    };
    
    checkAdminStatus();
  }, [user]);

  useEffect(() => {
    if (hasAdminAccess) {
      fetchUsers();
      fetchStats();
    }
  }, [hasAdminAccess, page, searchQuery, filterDept, filterCollege, filterYear]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: (page * limit).toString(),
        limit: limit.toString(),
      });

      if (searchQuery) params.append("search", searchQuery);
      if (filterDept) params.append("department", filterDept);
      if (filterCollege) params.append("college", filterCollege);
      if (filterYear) params.append("year", filterYear);

      const data = await apiRequest<{ users: User[]; total: number }>(
        `/api/admin/users?${params.toString()}`
      );

      setUsers(data.users);
      setTotal(data.total);
    } catch (error: any) {
      showToast(error.message || "Failed to fetch users", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await apiRequest<UserStats>("/api/admin/users/stats");
      setStats(data);
    } catch (error: any) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const handleDelete = async (userId: string, usn: string) => {
    if (!confirm(`Are you sure you want to delete user ${usn}? This cannot be undone.`)) {
      return;
    }

    try {
      await apiRequest(`/api/admin/users/${userId}`, { method: "DELETE" });
      showToast("User deleted successfully", "success");
      fetchUsers();
      fetchStats();
    } catch (error: any) {
      showToast(error.message || "Failed to delete user", "error");
    }
  };

  const handleExport = () => {
    const csv = [
      ["USN", "Email", "Department", "College", "Year", "Created At"].join(","),
      ...users.map((u) =>
        [u.usn, u.email, u.department, u.college, u.year, u.createdAt].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `users_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const clearFilters = () => {
    setSearchQuery("");
    setFilterDept("");
    setFilterCollege("");
    setFilterYear("");
    setPage(0);
  };

  if (checkingAdmin) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <RefreshCw className="h-16 w-16 text-blue-500 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Checking Access...</h2>
          <p className="text-slate-600">Please wait while we verify your permissions.</p>
        </div>
      </div>
    );
  }

  if (!hasAdminAccess) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <Shield className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Access Denied</h2>
          <p className="text-slate-600">
            You don't have permission to access the admin panel.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-slate-900 rounded-lg flex items-center justify-center">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-slate-900">Admin Panel</h1>
                <p className="text-slate-600 text-lg">Management Dashboard</p>
              </div>
            </div>
            <Button onClick={fetchUsers} variant="outline" size="lg">
              <RefreshCw className="mr-2 h-5 w-5" />
              Refresh
            </Button>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-slate-200">
            <button
              onClick={() => setActiveTab('users')}
              className={`px-6 py-3 font-semibold transition-colors flex items-center gap-2 ${
                activeTab === 'users'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Users className="w-5 h-5" />
              User Management
            </button>
            <button
              onClick={() => setActiveTab('feedback')}
              className={`px-6 py-3 font-semibold transition-colors flex items-center gap-2 ${
                activeTab === 'feedback'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              Beta Feedback
            </button>
          </div>

          {/* User Management Tab */}
          {activeTab === 'users' && (
            <>
              {/* Stats Cards */}
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-600 text-sm font-medium">Total Users</p>
                    <p className="text-3xl font-bold text-slate-900 mt-2">{stats.total_users}</p>
                  </div>
                  <Users className="h-10 w-10 text-blue-600" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-600 text-sm font-medium">Departments</p>
                    <p className="text-3xl font-bold text-slate-900 mt-2">{stats.by_department.length}</p>
                  </div>
                  <BarChart3 className="h-10 w-10 text-green-600" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-600 text-sm font-medium">New (7 Days)</p>
                    <p className="text-3xl font-bold text-slate-900 mt-2">{stats.recent_signups_7d}</p>
                  </div>
                  <Users className="h-10 w-10 text-purple-600" />
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-600 text-sm font-medium">Colleges</p>
                    <p className="text-3xl font-bold text-slate-900 mt-2">{stats.by_college.length}</p>
                  </div>
                  <BarChart3 className="h-10 w-10 text-orange-600" />
                </div>
              </div>
            </div>
              )}

              {/* Search and Filters */}
              <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-2 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by USN or email..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setPage(0);
                  }}
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <select
                value={filterDept}
                onChange={(e) => {
                  setFilterDept(e.target.value);
                  setPage(0);
                }}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Departments</option>
                <option value="CSE">CSE</option>
                <option value="ISE">ISE</option>
                <option value="ECE">ECE</option>
                <option value="EEE">EEE</option>
                <option value="MECH">MECH</option>
                <option value="AIML">AIML</option>
              </select>
              <select
                value={filterYear}
                onChange={(e) => {
                  setFilterYear(e.target.value);
                  setPage(0);
                }}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Years</option>
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
              </select>
              <div className="flex gap-2">
                <Button onClick={clearFilters} variant="outline" className="flex-1">
                  <X className="mr-2 h-4 w-4" />
                  Clear
                </Button>
                <Button onClick={handleExport} variant="outline" className="flex-1">
                  <Download className="mr-2 h-4 w-4" />
                  Export
                </Button>
              </div>
            </div>
              </div>

              {/* Users Table */}
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">USN</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Email</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Department</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Year</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">College</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">Joined</th>
                  <th className="px-6 py-4 text-right text-sm font-semibold text-slate-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                      <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
                      Loading users...
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                      No users found
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 text-sm font-medium text-slate-900">{user.usn}</td>
                      <td className="px-6 py-4 text-sm text-slate-600">{user.email}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {user.department}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">Year {user.year}</td>
                      <td className="px-6 py-4 text-sm text-slate-600 uppercase">{user.college}</td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {new Date(user.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleDelete(user.id, user.usn)}
                          className="text-red-600 hover:text-red-800 transition-colors"
                          title="Delete user"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
                </table>
                </div>

                {/* Pagination */}
                {total > limit && (
                  <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between">
              <div className="text-sm text-slate-600">
                Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total} users
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 0}
                  variant="outline"
                  size="sm"
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(page + 1)}
                  disabled={(page + 1) * limit >= total}
                  variant="outline"
                  size="sm"
                >
                  Next
                </Button>
                  </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Feedback Management Tab */}
          {activeTab === 'feedback' && (
            <FeedbackManagement />
          )}
        </div>
      </div>
    </div>
  );
}

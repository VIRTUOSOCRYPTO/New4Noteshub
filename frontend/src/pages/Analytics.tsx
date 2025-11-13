import { useState, useEffect } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, TrendingUp, Users, FileText, Download, Eye, Activity } from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from "recharts";
import { showToast } from "@/components/ui/toast-container";
import { PageSkeleton } from "@/components/loading/SkeletonLoaders";
import { DEPARTMENTS } from "@/lib/constants";

interface DashboardStats {
  total_notes: number;
  total_users: number;
  active_users: number;
  total_downloads: number;
  total_views: number;
  avg_downloads_per_note: number;
  avg_views_per_note: number;
  uploads: {
    last_24h: number;
    last_7d: number;
    last_30d: number;
  };
}

interface Note {
  id: string;
  title: string;
  subject: string;
  department: string;
  download_count: number;
  view_count: number;
  popularity_score: number;
}

interface DepartmentStat {
  department: string;
  total_notes: number;
  total_downloads: number;
  total_views: number;
  avg_downloads: number;
  avg_views: number;
}

interface TrendData {
  date: string;
  uploads: number;
}

interface Prediction {
  date: string;
  predicted_uploads: number;
  confidence: string;
}

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [popularNotes, setPopularNotes] = useState<Note[]>([]);
  const [departmentStats, setDepartmentStats] = useState<DepartmentStat[]>([]);
  const [uploadTrends, setUploadTrends] = useState<TrendData[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string | undefined>(undefined);
  const [trendDays, setTrendDays] = useState(30);

  useEffect(() => {
    loadAnalytics();
  }, [selectedDepartment, trendDays]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);

      // Load dashboard stats
      const statsUrl = selectedDepartment 
        ? `/api/analytics/dashboard?department=${selectedDepartment}`
        : "/api/analytics/dashboard";
      const stats = await apiRequest<DashboardStats>(statsUrl);
      setDashboardStats(stats);

      // Load popular notes
      const popularUrl = selectedDepartment
        ? `/api/analytics/popular-notes?limit=10&department=${selectedDepartment}`
        : "/api/analytics/popular-notes?limit=10";
      const popularData = await apiRequest<{ notes: Note[] }>(popularUrl);
      setPopularNotes(popularData.notes);

      // Load department statistics
      const deptData = await apiRequest<{ departments: DepartmentStat[] }>("/api/analytics/departments");
      setDepartmentStats(deptData.departments);

      // Load upload trends
      const trendsData = await apiRequest<{ trends: TrendData[] }>(
        `/api/analytics/trends/uploads?days=${trendDays}`
      );
      setUploadTrends(trendsData.trends);

      // Load predictions
      const predData = await apiRequest<{ predictions: Prediction[] }>(
        "/api/analytics/trends/predictions?days_ahead=7"
      );
      setPredictions(predData.predictions);

    } catch (error) {
      console.error("Error loading analytics:", error);
      showToast("Failed to load analytics data", "error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <PageSkeleton />;
  }

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#a4de6c', '#d0ed57'];

  return (
    <div className="container mx-auto px-4 py-8" data-testid="analytics-dashboard">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800" data-testid="analytics-title">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600 mt-2">Comprehensive insights and trends</p>
        </div>
        <Select value={selectedDepartment || "all"} onValueChange={(val) => setSelectedDepartment(val === "all" ? undefined : val)}>
          <SelectTrigger className="w-[200px]" aria-label="Filter by department">
            <SelectValue placeholder="All Departments" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Departments</SelectItem>
            {DEPARTMENTS.map((dept) => (
              <SelectItem key={dept.value} value={dept.value}>
                {dept.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Stats Cards */}
      {dashboardStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card data-testid="stat-card-notes">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Notes</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats.total_notes}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardStats.uploads.last_7d} uploaded this week
              </p>
            </CardContent>
          </Card>

          <Card data-testid="stat-card-downloads">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Downloads</CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats.total_downloads}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardStats.avg_downloads_per_note.toFixed(1)} avg per note
              </p>
            </CardContent>
          </Card>

          <Card data-testid="stat-card-views">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Views</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats.total_views}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardStats.avg_views_per_note.toFixed(1)} avg per note
              </p>
            </CardContent>
          </Card>

          <Card data-testid="stat-card-users">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardStats.active_users}</div>
              <p className="text-xs text-muted-foreground">
                of {dashboardStats.total_users} total users
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs for different views */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList aria-label="Analytics sections">
          <TabsTrigger value="trends" data-testid="tab-trends">Trends & Predictions</TabsTrigger>
          <TabsTrigger value="popular" data-testid="tab-popular">Popular Notes</TabsTrigger>
          <TabsTrigger value="departments" data-testid="tab-departments">Departments</TabsTrigger>
        </TabsList>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" aria-hidden="true" />
                  Upload Trends
                </CardTitle>
                <CardDescription>Last {trendDays} days</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={uploadTrends}>
                    <defs>
                      <linearGradient id="colorUploads" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="uploads" stroke="#8884d8" fillOpacity={1} fill="url(#colorUploads)" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" aria-hidden="true" />
                  Predictions (7 days)
                </CardTitle>
                <CardDescription>AI-powered trend forecasting</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={predictions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="predicted_uploads" stroke="#82ca9d" strokeWidth={2} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Popular Notes Tab */}
        <TabsContent value="popular">
          <Card>
            <CardHeader>
              <CardTitle>Top 10 Popular Notes</CardTitle>
              <CardDescription>Ranked by downloads and views</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {popularNotes.map((note, index) => (
                  <div key={note.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors" data-testid={`popular-note-${index}`}>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-800">{note.title}</h4>
                        <p className="text-sm text-gray-600">
                          {note.subject} • {note.department}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <Download className="h-4 w-4 text-gray-500" aria-hidden="true" />
                        <span>{note.download_count}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4 text-gray-500" aria-hidden="true" />
                        <span>{note.view_count}</span>
                      </div>
                    </div>
                  </div>
                ))}
                {popularNotes.length === 0 && (
                  <p className="text-center text-gray-500 py-8">No popular notes yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Departments Tab */}
        <TabsContent value="departments">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Department Statistics</CardTitle>
                <CardDescription>Notes distribution by department</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={departmentStats}
                      dataKey="total_notes"
                      nameKey="department"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label
                    >
                      {departmentStats.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Department Performance</CardTitle>
                <CardDescription>Downloads by department</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={departmentStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="total_downloads" fill="#8884d8" />
                    <Bar dataKey="total_views" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Department Details Table */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Department Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full" role="table">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4" scope="col">Department</th>
                      <th className="text-right p-4" scope="col">Notes</th>
                      <th className="text-right p-4" scope="col">Downloads</th>
                      <th className="text-right p-4" scope="col">Views</th>
                      <th className="text-right p-4" scope="col">Avg Downloads</th>
                    </tr>
                  </thead>
                  <tbody>
                    {departmentStats.map((dept) => (
                      <tr key={dept.department} className="border-b hover:bg-gray-50">
                        <td className="p-4 font-medium">{dept.department}</td>
                        <td className="p-4 text-right">{dept.total_notes}</td>
                        <td className="p-4 text-right">{dept.total_downloads}</td>
                        <td className="p-4 text-right">{dept.total_views}</td>
                        <td className="p-4 text-right">{dept.avg_downloads.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

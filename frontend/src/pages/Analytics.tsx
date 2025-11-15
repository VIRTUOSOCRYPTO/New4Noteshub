import { useState, useEffect } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, TrendingUp, Users, FileText, Download, Eye, Activity, Award, Target } from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from "recharts";
import { showToast } from "@/components/ui/toast-container";
import { PageSkeleton } from "@/components/loading/SkeletonLoaders";
import { DEPARTMENTS } from "@/lib/constants";
import { motion } from "framer-motion";

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
  downloadCount: number;
  viewCount: number;
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

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

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

      const statsUrl = selectedDepartment 
        ? `/api/analytics/dashboard?department=${selectedDepartment}`
        : "/api/analytics/dashboard";
      const stats = await apiRequest<DashboardStats>(statsUrl);
      setDashboardStats(stats);

      const popularUrl = selectedDepartment
        ? `/api/analytics/popular-notes?limit=10&department=${selectedDepartment}`
        : "/api/analytics/popular-notes?limit=10";
      const popularData = await apiRequest<{ notes: Note[] }>(popularUrl);
      setPopularNotes(popularData.notes);

      const deptData = await apiRequest<{ departments: DepartmentStat[] }>("/api/analytics/departments");
      setDepartmentStats(deptData.departments);

      const trendsData = await apiRequest<{ trends: TrendData[] }>(
        `/api/analytics/trends/uploads?days=${trendDays}`
      );
      setUploadTrends(trendsData.trends);

      const predData = await apiRequest<{ predictions: Prediction[] }>(
        "/api/analytics/trends/predictions?days_ahead=7"
      );
      setPredictions(predData.predictions);

      setLoading(false);
    } catch (error: any) {
      console.error("Failed to load analytics:", error);
      showToast(error.message || "Failed to load analytics", "error");
      setLoading(false);
    }
  };

  if (loading) {
    return <PageSkeleton />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          className="absolute top-20 left-10 w-40 h-40 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full opacity-20 blur-3xl"
          animate={{ y: [0, -30, 0], x: [0, 20, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-20 right-20 w-56 h-56 bg-gradient-to-br from-pink-400 to-orange-500 rounded-full opacity-20 blur-3xl"
          animate={{ y: [0, 30, 0], x: [0, -20, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <div className="container mx-auto px-4 py-12 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
            <div className="flex items-center space-x-4 mb-4 md:mb-0">
              <motion.div
                whileHover={{ rotate: 360, scale: 1.1 }}
                transition={{ duration: 0.5 }}
                className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg"
              >
                <BarChart3 className="h-8 w-8 text-white" />
              </motion.div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                  Analytics Dashboard
                </h1>
                <p className="text-gray-600 text-lg mt-1">Real-time insights and performance metrics</p>
              </div>
            </div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white/80 backdrop-blur-xl rounded-xl p-4 shadow-lg border border-white/20"
            >
              <label className="text-sm font-medium text-gray-700 mb-2 block">Filter by Department</label>
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="All Departments" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  {DEPARTMENTS.map(dept => (
                    <SelectItem key={dept.value} value={dept.value}>{dept.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </motion.div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        {dashboardStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            {[
              { 
                label: "Total Notes", 
                value: dashboardStats.total_notes.toLocaleString(), 
                icon: FileText, 
                color: "from-blue-500 to-cyan-500",
                change: `+${dashboardStats.uploads.last_7d} this week`
              },
              { 
                label: "Total Users", 
                value: dashboardStats.total_users.toLocaleString(), 
                icon: Users, 
                color: "from-purple-500 to-pink-500",
                change: `${dashboardStats.active_users} active`
              },
              { 
                label: "Total Downloads", 
                value: dashboardStats.total_downloads.toLocaleString(), 
                icon: Download, 
                color: "from-orange-500 to-red-500",
                change: `Avg ${dashboardStats.avg_downloads_per_note.toFixed(1)} per note`
              },
              { 
                label: "Total Views", 
                value: dashboardStats.total_views.toLocaleString(), 
                icon: Eye, 
                color: "from-green-500 to-teal-500",
                change: `Avg ${dashboardStats.avg_views_per_note.toFixed(1)} per note`
              }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-lg hover:shadow-2xl transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                        <stat.icon className="h-6 w-6 text-white" />
                      </div>
                      <TrendingUp className="h-5 w-5 text-green-500" />
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-600 mb-2">{stat.label}</div>
                    <div className="text-xs text-gray-500">{stat.change}</div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Charts Section */}
        <Tabs defaultValue="trends" className="space-y-6">
          <TabsList className="bg-white/80 backdrop-blur-xl border border-white/20 shadow-lg">
            <TabsTrigger value="trends">Upload Trends</TabsTrigger>
            <TabsTrigger value="popular">Popular Notes</TabsTrigger>
            <TabsTrigger value="departments">Departments</TabsTrigger>
            <TabsTrigger value="predictions">Predictions</TabsTrigger>
          </TabsList>

          <TabsContent value="trends">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="text-2xl">Upload Trends</CardTitle>
                      <CardDescription>Track upload activity over time</CardDescription>
                    </div>
                    <Select value={trendDays.toString()} onValueChange={(v) => setTrendDays(Number(v))}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="7">Last 7 Days</SelectItem>
                        <SelectItem value="30">Last 30 Days</SelectItem>
                        <SelectItem value="90">Last 90 Days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={uploadTrends}>
                      <defs>
                        <linearGradient id="colorUploads" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="date" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                          backdropFilter: 'blur(10px)',
                          borderRadius: '12px',
                          border: '1px solid rgba(139, 92, 246, 0.2)'
                        }} 
                      />
                      <Area type="monotone" dataKey="uploads" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorUploads)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="popular">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center">
                    <Award className="h-6 w-6 text-yellow-500 mr-2" />
                    Top Performing Notes
                  </CardTitle>
                  <CardDescription>Most popular notes by engagement</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {popularNotes.map((note, index) => (
                      <motion.div
                        key={note.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                        whileHover={{ scale: 1.02, x: 10 }}
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-white to-purple-50 rounded-xl border border-purple-100 hover:shadow-lg transition-all duration-300"
                      >
                        <div className="flex items-center space-x-4 flex-1">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white ${
                            index === 0 ? 'bg-gradient-to-br from-yellow-400 to-orange-500' :
                            index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                            index === 2 ? 'bg-gradient-to-br from-orange-400 to-red-500' :
                            'bg-gradient-to-br from-purple-400 to-pink-500'
                          }`}>
                            {index + 1}
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900">{note.title}</div>
                            <div className="text-sm text-gray-600">{note.department} • {note.subject}</div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-6 text-sm">
                          <div className="text-center">
                            <div className="font-bold text-blue-600">{note.downloadCount}</div>
                            <div className="text-gray-500 text-xs">Downloads</div>
                          </div>
                          <div className="text-center">
                            <div className="font-bold text-purple-600">{note.viewCount}</div>
                            <div className="text-gray-500 text-xs">Views</div>
                          </div>
                          <div className="text-center">
                            <div className="font-bold text-green-600">{note.popularity_score.toFixed(1)}</div>
                            <div className="text-gray-500 text-xs">Score</div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="departments">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl">Notes by Department</CardTitle>
                  <CardDescription>Distribution across departments</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie
                        data={departmentStats}
                        dataKey="total_notes"
                        nameKey="department"
                        cx="50%"
                        cy="50%"
                        outerRadius={120}
                        label
                      >
                        {departmentStats.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                          backdropFilter: 'blur(10px)',
                          borderRadius: '12px'
                        }} 
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl">Department Performance</CardTitle>
                  <CardDescription>Downloads and views by department</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={departmentStats}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="department" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                          backdropFilter: 'blur(10px)',
                          borderRadius: '12px'
                        }} 
                      />
                      <Legend />
                      <Bar dataKey="total_downloads" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="total_views" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="predictions">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl flex items-center">
                    <Target className="h-6 w-6 text-blue-500 mr-2" />
                    Upload Predictions
                  </CardTitle>
                  <CardDescription>AI-powered forecast for next 7 days</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={predictions}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="date" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                          backdropFilter: 'blur(10px)',
                          borderRadius: '12px',
                          border: '1px solid rgba(59, 130, 246, 0.2)'
                        }} 
                      />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="predicted_uploads" 
                        stroke="#3b82f6" 
                        strokeWidth={3}
                        strokeDasharray="5 5"
                        dot={{ fill: '#3b82f6', r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

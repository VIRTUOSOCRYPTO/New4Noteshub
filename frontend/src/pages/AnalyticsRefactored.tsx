/**
 * Analytics Page (Refactored)
 * Split into smaller, reusable components following SRP
 */

import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  DashboardStats,
  UploadTrendsChart,
  PopularNotesTable,
  DepartmentStatsChart
} from '@/components/analytics';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

// API Functions
async function fetchDashboardStats() {
  const response = await fetch(`${BACKEND_URL}/api/analytics/dashboard`, {
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Failed to fetch dashboard stats');
  return response.json();
}

async function fetchUploadTrends() {
  const response = await fetch(`${BACKEND_URL}/api/analytics/trends/uploads?days=30`, {
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Failed to fetch upload trends');
  return response.json();
}

async function fetchPopularNotes() {
  const response = await fetch(`${BACKEND_URL}/api/analytics/popular-notes?limit=10`, {
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Failed to fetch popular notes');
  return response.json();
}

async function fetchDepartmentStats() {
  const response = await fetch(`${BACKEND_URL}/api/analytics/departments`, {
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Failed to fetch department stats');
  return response.json();
}

export default function AnalyticsRefactored() {
  // Fetch all data using React Query
  const { data: dashboardData, isLoading: loadingDashboard, error: dashboardError } = useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: fetchDashboardStats
  });

  const { data: trendsData, isLoading: loadingTrends } = useQuery({
    queryKey: ['analytics', 'trends'],
    queryFn: fetchUploadTrends
  });

  const { data: popularNotesData, isLoading: loadingPopular } = useQuery({
    queryKey: ['analytics', 'popular'],
    queryFn: fetchPopularNotes
  });

  const { data: departmentData, isLoading: loadingDepartments } = useQuery({
    queryKey: ['analytics', 'departments'],
    queryFn: fetchDepartmentStats
  });

  // Loading state
  if (loadingDashboard) {
    return (
      <div className=\"flex items-center justify-center min-h-screen\">
        <Loader2 className=\"h-8 w-8 animate-spin\" />
      </div>
    );
  }

  // Error state
  if (dashboardError) {
    return (
      <div className=\"container mx-auto px-4 py-8\">
        <Alert variant=\"destructive\">
          <AlertDescription>
            Failed to load analytics data. Please try again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className=\"container mx-auto px-4 py-8\" data-testid=\"analytics-page\">
      <h1 className=\"text-3xl font-bold mb-8\">Analytics Dashboard</h1>

      {/* Dashboard Stats */}
      <div className=\"mb-8\">
        <DashboardStats stats={dashboardData} />
      </div>

      {/* Upload Trends Chart */}
      {loadingTrends ? (
        <div className=\"flex justify-center p-8\">
          <Loader2 className=\"h-6 w-6 animate-spin\" />
        </div>
      ) : trendsData?.trends && (
        <div className=\"mb-8\">
          <UploadTrendsChart data={trendsData.trends} />
        </div>
      )}

      {/* Grid Layout for Charts and Table */}
      <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8\">
        {/* Department Stats */}
        {loadingDepartments ? (
          <div className=\"flex justify-center p-8\">
            <Loader2 className=\"h-6 w-6 animate-spin\" />
          </div>
        ) : departmentData?.departments && (
          <DepartmentStatsChart data={departmentData.departments} />
        )}

        {/* Popular Notes */}
        {loadingPopular ? (
          <div className=\"flex justify-center p-8\">
            <Loader2 className=\"h-6 w-6 animate-spin\" />
          </div>
        ) : popularNotesData?.notes && (
          <PopularNotesTable notes={popularNotesData.notes} />
        )}
      </div>
    </div>
  );
}

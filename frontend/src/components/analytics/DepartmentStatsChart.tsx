import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface DepartmentStatsChartProps {
  data: Array<{
    department: string;
    notes: number;
    users: number;
  }>;
}

export function DepartmentStatsChart({ data }: DepartmentStatsChartProps) {
  return (
    <Card data-testid="department-stats-chart">
      <CardHeader>
        <CardTitle>Department Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="department" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="notes" fill="#3b82f6" name="Notes" />
            <Bar dataKey="users" fill="#10b981" name="Users" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

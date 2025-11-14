import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, FileText, Download, Eye } from 'lucide-react';

interface DashboardStatsProps {
  stats: {
    totalNotes: number;
    totalUsers: number;
    totalDownloads: number;
    totalViews: number;
  };
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  const statCards = [
    {
      title: 'Total Notes',
      value: stats.totalNotes,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Total Users',
      value: stats.totalUsers,
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Total Downloads',
      value: stats.totalDownloads,
      icon: Download,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Total Views',
      value: stats.totalViews,
      icon: Eye,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="dashboard-stats">
      {statCards.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card key={stat.title} data-testid={`stat-card-${stat.title.toLowerCase().replace(' ', '-')}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className={`${stat.bgColor} p-2 rounded-lg`}>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" data-testid={`stat-value-${stat.title.toLowerCase().replace(' ', '-')}`}>
                {stat.value.toLocaleString()}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

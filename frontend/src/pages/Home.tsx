import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { BookOpen, Search, Upload, Users, Shield, TrendingUp, Building2, CheckCircle, ArrowRight, BarChart3 } from "lucide-react";
import HomeShareOptions from "@/components/home/HomeShareOptions";
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import { Note } from "@/lib/schema";
import { usePageVisits } from "@/hooks/use-page-visits";

export default function Home() {
  usePageVisits('home');
  const [, navigate] = useLocation();
  const { user } = useAuth();
  
  const allowedDepartments = ['CSE', 'ISE', 'AIML', 'ECE'];
  const hasAccessToModeration = user && allowedDepartments.includes(user.department);
  
  const { data: flaggedNotes } = useQuery({
    queryKey: ['/api/notes/flagged'],
    queryFn: async () => {
      if (!hasAccessToModeration) return [];
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/notes/flagged', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) return [];
      return response.json() as Promise<Note[]>;
    },
    enabled: !!hasAccessToModeration,
    refetchInterval: 60000
  });

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white overflow-hidden">
        {/* Subtle Pattern Overlay */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
        
        <div className="container mx-auto px-4 py-20 md:py-32 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 bg-blue-500/20 border border-blue-400/30 rounded-full px-6 py-2 mb-8">
              <Shield className="h-4 w-4" />
              <span className="text-sm font-medium">Enterprise-Grade Academic Platform</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Knowledge Management
              <br />
              <span className="text-blue-400">For Modern Education</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-2xl mx-auto">
              Streamline academic content sharing with enterprise security, 
              structured organization, and institutional-grade reliability.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg h-auto"
                onClick={() => navigate("/find")}
              >
                <Search className="mr-2 h-5 w-5" />
                Browse Repository
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              
              <Button
                size="lg"
                className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-6 text-lg h-auto"
                onClick={() => navigate("/upload")}
              >
                <Upload className="mr-2 h-5 w-5" />
                Contribute Content
              </Button>
            </div>

            {/* Stats Bar */}
            <div className="grid grid-cols-3 gap-8 mt-16 pt-12 border-t border-white/10">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">10,000+</div>
                <div className="text-slate-400 text-sm uppercase tracking-wide">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">50,000+</div>
                <div className="text-slate-400 text-sm uppercase tracking-wide">Resources</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">98%</div>
                <div className="text-slate-400 text-sm uppercase tracking-wide">Satisfaction</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Enterprise Features
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Built for institutions that demand reliability, security, and scalability
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Shield,
                title: "Secure Infrastructure",
                description: "Bank-level encryption and data protection protocols",
                color: "text-blue-600"
              },
              {
                icon: Building2,
                title: "Department Management",
                description: "Organized by departments with role-based access",
                color: "text-slate-600"
              },
              {
                icon: BarChart3,
                title: "Analytics Dashboard",
                description: "Track engagement and content performance metrics",
                color: "text-blue-600"
              },
              {
                icon: CheckCircle,
                title: "Quality Assurance",
                description: "Automated validation and content review systems",
                color: "text-slate-600"
              }
            ].map((feature, index) => (
              <div 
                key={index} 
                className="bg-slate-50 rounded-lg p-8 border border-slate-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200"
              >
                <div className={`w-14 h-14 ${feature.color} bg-slate-100 rounded-lg flex items-center justify-center mb-6`}>
                  <feature.icon className="h-7 w-7" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Streamlined Workflow
            </h2>
            <p className="text-xl text-slate-600">
              Three simple steps to knowledge sharing
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            {[
              { 
                step: "01", 
                icon: BookOpen, 
                title: "Access Repository", 
                description: "Browse organized collections by department and subject matter"
              },
              { 
                step: "02", 
                icon: Upload, 
                title: "Contribute Content", 
                description: "Upload and share your academic resources with validation"
              },
              { 
                step: "03", 
                icon: TrendingUp, 
                title: "Track Performance", 
                description: "Monitor engagement and impact through analytics"
              }
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="bg-white rounded-lg p-8 shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
                  <div className="text-6xl font-bold text-slate-200 mb-4">{item.step}</div>
                  <div className="w-14 h-14 bg-slate-900 rounded-lg flex items-center justify-center mb-6">
                    <item.icon className="h-7 w-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-3">{item.title}</h3>
                  <p className="text-slate-600">{item.description}</p>
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-6 transform -translate-y-1/2">
                    <ArrowRight className="h-6 w-6 text-slate-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">
                  Trusted by Leading Institutions
                </h2>
                <p className="text-lg text-slate-600 mb-8">
                  NotesHub provides the infrastructure and security that educational institutions 
                  need to manage academic content at scale.
                </p>
                <div className="space-y-4">
                  {[
                    "ISO 27001 Certified Security",
                    "99.9% Uptime SLA",
                    "24/7 Technical Support",
                    "GDPR Compliant"
                  ].map((item, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0" />
                      <span className="text-slate-700">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="bg-slate-50 rounded-lg p-12 border-2 border-slate-200">
                <div className="grid grid-cols-2 gap-8">
                  <div className="text-center">
                    <Users className="h-10 w-10 text-slate-600 mx-auto mb-3" />
                    <div className="text-3xl font-bold text-slate-900 mb-1">10K+</div>
                    <div className="text-sm text-slate-600">Active Users</div>
                  </div>
                  <div className="text-center">
                    <BookOpen className="h-10 w-10 text-slate-600 mx-auto mb-3" />
                    <div className="text-3xl font-bold text-slate-900 mb-1">50K+</div>
                    <div className="text-sm text-slate-600">Resources</div>
                  </div>
                  <div className="text-center">
                    <Building2 className="h-10 w-10 text-slate-600 mx-auto mb-3" />
                    <div className="text-3xl font-bold text-slate-900 mb-1">12+</div>
                    <div className="text-sm text-slate-600">Departments</div>
                  </div>
                  <div className="text-center">
                    <TrendingUp className="h-10 w-10 text-slate-600 mx-auto mb-3" />
                    <div className="text-3xl font-bold text-slate-900 mb-1">98%</div>
                    <div className="text-sm text-slate-600">Satisfaction</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-slate-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Join thousands of users leveraging enterprise-grade knowledge management
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg h-auto"
                onClick={() => navigate("/upload")}
              >
                Start Contributing
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <HomeShareOptions />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

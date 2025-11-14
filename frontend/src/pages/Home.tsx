import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { BookOpen, Search, Upload, Users, BookText, Lightbulb, AlertTriangle, ArrowRight, Star, TrendingUp, Shield, Zap } from "lucide-react";
import HomeShareOptions from "@/components/home/HomeShareOptions";
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import { Note } from "@/lib/schema";
import { usePageVisits } from "@/hooks/use-page-visits";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function Home() {
  usePageVisits('home');
  const [, navigate] = useLocation();
  const { user } = useAuth();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
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

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.3 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 100 }
    }
  };

  const floatingAnimation = {
    y: [0, -20, 0],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  return (
    <div className="flex flex-col min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" />
        <motion.div
          className="absolute inset-0 opacity-30"
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse"
          }}
          style={{
            backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.1) 0%, transparent 50%)',
            backgroundSize: '100% 100%'
          }}
        />
      </div>

      {/* Hero Section */}
      <section className="relative py-20 md:py-32 overflow-hidden">
        {/* Floating Elements */}
        <motion.div
          className="absolute top-20 left-10 w-20 h-20 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full opacity-20 blur-xl"
          animate={{ y: [0, -30, 0], x: [0, 20, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-32 h-32 bg-gradient-to-br from-pink-400 to-orange-500 rounded-full opacity-20 blur-xl"
          animate={{ y: [0, 30, 0], x: [0, -20, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />

        <div className="container mx-auto px-4 relative z-10">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <motion.div
              initial="hidden"
              animate="visible"
              variants={containerVariants}
            >
              <motion.div variants={itemVariants} className="inline-block mb-4">
                <span className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm font-semibold rounded-full shadow-lg">
                  🚀 Welcome to the Future of Learning
                </span>
              </motion.div>
              
              <motion.h1
                variants={itemVariants}
                className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
              >
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 animate-gradient">
                  Share Knowledge,
                </span>
                <br />
                <span className="text-gray-900">Achieve Together</span>
              </motion.h1>
              
              <motion.p
                variants={itemVariants}
                className="text-xl text-gray-700 mb-8 leading-relaxed"
              >
                Join thousands of students collaborating, sharing notes, and excelling together.
                Your academic success starts here.
              </motion.p>
              
              <motion.div
                variants={itemVariants}
                className="flex flex-col sm:flex-row gap-4"
              >
                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    size="lg"
                    className="px-8 py-6 text-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-xl hover:shadow-2xl transition-all duration-300"
                    onClick={() => navigate("/find")}
                  >
                    <Search className="mr-2 h-6 w-6" />
                    Explore Notes
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </motion.div>
                
                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    size="lg"
                    variant="outline"
                    className="px-8 py-6 text-lg border-2 border-purple-300 hover:bg-purple-50 hover:border-purple-400 transition-all duration-300"
                    onClick={() => navigate("/upload")}
                  >
                    <Upload className="mr-2 h-6 w-6" />
                    Share Your Notes
                  </Button>
                </motion.div>
              </motion.div>

              {/* Stats */}
              <motion.div
                variants={itemVariants}
                className="grid grid-cols-3 gap-6 mt-12"
              >
                {[
                  { label: "Active Students", value: "10K+", icon: Users },
                  { label: "Notes Shared", value: "50K+", icon: BookOpen },
                  { label: "Success Rate", value: "98%", icon: TrendingUp }
                ].map((stat, i) => (
                  <motion.div
                    key={i}
                    whileHover={{ scale: 1.1, y: -5 }}
                    className="text-center"
                  >
                    <stat.icon className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                    <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>

            {/* Hero Image */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, rotateY: -30 }}
              animate={{ opacity: 1, scale: 1, rotateY: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="relative"
            >
              <motion.div
                animate={floatingAnimation}
                className="relative"
              >
                <div className="absolute -inset-4 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-3xl blur-2xl opacity-30" />
                <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/20">
                  <img
                    src="https://images.unsplash.com/photo-1758270705317-3ef6142d306f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHw0fHxzdHVkZW50cyUyMGNvbGxhYm9yYXRpb258ZW58MHx8fHwxNzYzMTI3NzI2fDA&ixlib=rb-4.1.0&q=85"
                    alt="Students collaborating"
                    className="w-full h-auto rounded-3xl"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-purple-900/20 to-transparent" />
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                Why Choose NotesHub?
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience seamless collaboration with powerful features designed for students
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Search,
                title: "Smart Search",
                description: "Find exactly what you need with AI-powered search and filters",
                gradient: "from-blue-500 to-cyan-500"
              },
              {
                icon: Shield,
                title: "Secure & Safe",
                description: "Your data is protected with enterprise-grade security",
                gradient: "from-purple-500 to-pink-500"
              },
              {
                icon: Zap,
                title: "Lightning Fast",
                description: "Optimized for speed with instant uploads and downloads",
                gradient: "from-orange-500 to-red-500"
              },
              {
                icon: Users,
                title: "Community Driven",
                description: "Connect with peers and build your academic network",
                gradient: "from-green-500 to-teal-500"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -10, scale: 1.05 }}
                className="group"
              >
                <div className="relative h-full">
                  <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl blur-xl" 
                       style={{ background: `linear-gradient(to bottom right, var(--tw-gradient-stops))` }} />
                  <div className="relative bg-white/80 backdrop-blur-xl rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-white/20 h-full">
                    <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className="h-8 w-8 text-white" />
                    </div>
                    <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gradient-to-br from-blue-50 to-purple-50 relative overflow-hidden">
        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900">
              Get Started in <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600">3 Simple Steps</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              { step: "01", icon: BookOpen, title: "Browse Notes", description: "Explore thousands of quality notes across all subjects" },
              { step: "02", icon: Upload, title: "Share Your Work", description: "Upload your notes and help fellow students succeed" },
              { step: "03", icon: Star, title: "Collaborate & Grow", description: "Build connections and achieve academic excellence together" }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                whileHover={{ scale: 1.05, y: -10 }}
                className="relative"
              >
                <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-white/20 text-center">
                  <div className="text-6xl font-bold text-purple-200 mb-4">{item.step}</div>
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 transform hover:rotate-12 transition-transform duration-300">
                    <item.icon className="h-10 w-10 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-gray-900">{item.title}</h3>
                  <p className="text-gray-600">{item.description}</p>
                </div>
                {index < 2 && (
                  <motion.div
                    animate={{ x: [0, 10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2"
                  >
                    <ArrowRight className="h-8 w-8 text-purple-400" />
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600"
          animate={{
            backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{ backgroundSize: '200% 200%' }}
        />
        
        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center text-white"
          >
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              Ready to Transform Your Learning?
            </h2>
            <p className="text-xl md:text-2xl mb-12 max-w-3xl mx-auto opacity-90">
              Join thousands of students who are already succeeding together
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-6">
              <motion.div
                whileHover={{ scale: 1.1, y: -5 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  size="lg"
                  className="px-12 py-8 text-xl bg-white text-purple-600 hover:bg-gray-100 shadow-2xl"
                  onClick={() => navigate("/upload")}
                >
                  Start Sharing Now
                  <ArrowRight className="ml-2 h-6 w-6" />
                </Button>
              </motion.div>
              <HomeShareOptions />
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}

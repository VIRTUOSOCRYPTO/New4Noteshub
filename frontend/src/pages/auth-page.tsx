import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { loginUserSchema, registerUserSchema, forgotPasswordSchema, KARNATAKA_COLLEGES, COLLEGE_CODES, VALID_YEARS } from "@/lib/schema";
import { useAuth } from "@/hooks/use-auth";
import { useState, useEffect } from "react";
import { Redirect, Link } from "wouter";
import { Loader2, GraduationCap, BookOpen, Mail, Shield, Check, Building2, Lock, TrendingUp } from "lucide-react";
import { DEPARTMENTS } from "@/lib/constants";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AuthPage() {
  const { user, loginMutation, registerMutation } = useAuth();
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");

  // Redirect if user is already logged in
  if (user) {
    return <Redirect to="/" />;
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Left Section - Hero */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 p-12 flex-col justify-between relative overflow-hidden">
        {/* Subtle Pattern Overlay */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
        
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-12">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <Building2 className="h-7 w-7 text-white" />
            </div>
            <span className="text-3xl font-bold text-white">NotesHub</span>
          </div>
          
          <div className="max-w-md">
            <h1 className="text-4xl font-bold text-white mb-4 leading-tight">
              Your College's Digital Library
            </h1>
            <p className="text-lg text-slate-300 mb-12">
              Access notes from all departments within your college. Connect with your campus 
              community and share knowledge across departments.
            </p>
            
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Gamified Learning</h3>
                  <p className="text-slate-400 text-sm">Track progress with achievements and performance leaderboards</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BookOpen className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Campus Library</h3>
                  <p className="text-slate-400 text-sm">Access notes from all departments in your college</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Check className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-white font-semibold mb-1">Campus Collaboration</h3>
                  <p className="text-slate-400 text-sm">Study groups with students from your own college</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="relative z-10 text-slate-400 text-sm">
          <p>© 2025 NotesHub. All rights reserved.</p>
        </div>
      </div>

      {/* Right Section - Auth Forms */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-12">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <div className="lg:hidden flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-slate-900">NotesHub</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              {activeTab === "login" ? "Welcome Back" : "Create Your Account"}
            </h2>
            <p className="text-slate-600">
              {activeTab === "login" 
                ? "Access your college's knowledge hub" 
                : "Connect with students from your college across all departments"}
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as "login" | "register")} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8 bg-slate-200 p-1">
              <TabsTrigger 
                value="login" 
                className="data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-sm"
              >
                Sign In
              </TabsTrigger>
              <TabsTrigger 
                value="register"
                className="data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-sm"
              >
                Register
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="login" className="mt-0">
              <LoginForm />
            </TabsContent>
            
            <TabsContent value="register" className="mt-0">
              <RegisterForm />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

function LoginForm() {
  const { loginMutation } = useAuth();
  
  const form = useForm<z.infer<typeof loginUserSchema>>({
    resolver: zodResolver(loginUserSchema),
    defaultValues: {
      usn: "",
      password: ""
    }
  });
  
  const onSubmit = (data: z.infer<typeof loginUserSchema>) => {
    loginMutation.mutate(data, {
      onError: (error) => {
        if (error.message.includes("USN not registered")) {
          form.setError("usn", { 
            type: "manual", 
            message: "USN not registered. Please register first." 
          });
        } else if (error.message.includes("Incorrect password")) {
          form.setError("password", { 
            type: "manual", 
            message: "Incorrect password. Please try again." 
          });
        }
      }
    });
  };
  
  return (
    <Card className="border-slate-200 shadow-sm">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <CardContent className="space-y-4 pt-6">
            <FormField
              control={form.control}
              name="usn"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">University Seat Number</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="e.g., 1SI20CS045 or 22EC101" 
                      {...field}
                      onChange={(e) => field.onChange(e.target.value.toUpperCase())}
                      disabled={loginMutation.isPending}
                      className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">Password</FormLabel>
                  <FormControl>
                    <Input 
                      type="password" 
                      placeholder="Enter your password" 
                      {...field} 
                      disabled={loginMutation.isPending}
                      className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {loginMutation.error && !form.formState.errors.usn && !form.formState.errors.password && (
              <div className="text-red-600 text-sm p-3 border border-red-200 rounded-lg bg-red-50">
                {loginMutation.error.message}
              </div>
            )}
          </CardContent>
          
          <CardFooter className="flex flex-col gap-3">
            <Button 
              type="submit" 
              className="w-full bg-slate-900 hover:bg-slate-800 text-white" 
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Lock className="mr-2 h-4 w-4" />
              )}
              Sign In
            </Button>
            
            <ForgotPasswordDialog />
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}

function RegisterForm() {
  const { registerMutation } = useAuth();
  const [usnCode, setUsnCode] = useState<string>("");
  const [usnError, setUsnError] = useState<string | null>(null);
  const [collegeCode, setCollegeCode] = useState<string>("");
  const [customCollegeName, setCustomCollegeName] = useState<string>("");
  
  const form = useForm<z.infer<typeof registerUserSchema>>({
    resolver: zodResolver(registerUserSchema),
    defaultValues: {
      usn: "",
      email: "",
      department: "",
      college: "",
      year: undefined,
      password: "",
      confirmPassword: ""
    }
  });
  
  const handleUsnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase();
    form.setValue("usn", value);
    
    const standardPattern = /^[0-9]([A-Z]{2})([0-9]{2})([A-Z]{2})[0-9]{3}$/;
    const shortPattern = /^([0-9]{2})([A-Z]{2})[0-9]{3}$/;
    
    const upperValue = value.toUpperCase();
    const standardMatch = upperValue.match(standardPattern);
    const shortMatch = upperValue.match(shortPattern);
    
    if (standardMatch) {
      const collegeCode = standardMatch[1];
      const yearCode = standardMatch[2];
      const deptCode = standardMatch[3];
      
      setUsnCode(deptCode);
      setCollegeCode(collegeCode);
      
      const matchingDept = DEPARTMENTS.find(dept => dept.code === deptCode);
      
      if (COLLEGE_CODES[collegeCode]) {
        form.setValue("college", COLLEGE_CODES[collegeCode]);
      } else {
        form.setValue("college", "other");
        const defaultCollegeName = `${collegeCode} College`;
        setCustomCollegeName(defaultCollegeName);
      }
      
      const currentYear = new Date().getFullYear();
      const joiningYear = 2000 + parseInt(yearCode);
      let suggestedYear = currentYear - joiningYear + 1;
      
      if (suggestedYear >= 1 && suggestedYear <= 4) {
        const currentYearValue = form.getValues("year");
        if (currentYearValue === undefined) {
          form.setValue("year", suggestedYear);
        }
      }
      
      if (matchingDept) {
        form.setValue("department", matchingDept.value);
        setUsnError(null);
      } else {
        setUsnError(`Department code '${deptCode}' not recognized. Please check your USN.`);
      }
    } else if (shortMatch) {
      const yearCode = shortMatch[1];
      const deptCode = shortMatch[2];
      
      setUsnCode(deptCode);
      setCollegeCode("");
      
      const matchingDept = DEPARTMENTS.find(dept => dept.code === deptCode);
      
      form.setValue("college", "other");
      setCustomCollegeName("");
      
      const currentYear = new Date().getFullYear();
      const joiningYear = 2000 + parseInt(yearCode);
      let suggestedYear = currentYear - joiningYear + 1;
      
      if (suggestedYear >= 1 && suggestedYear <= 4) {
        const currentYearValue = form.getValues("year");
        if (currentYearValue === undefined) {
          form.setValue("year", suggestedYear);
        }
      }
      
      if (matchingDept) {
        form.setValue("department", matchingDept.value);
        setUsnError(null);
      } else {
        setUsnError(`Department code '${deptCode}' not recognized. Please check your USN.`);
      }
    } else if (value.length >= 7) {
      setUsnError("Invalid USN format. Examples: 1SI20CS045 or 22EC101");
      setUsnCode("");
      setCollegeCode("");
    } else {
      setUsnCode("");
      setCollegeCode("");
      setUsnError(null);
    }
  };
  
  const onSubmit = (data: z.infer<typeof registerUserSchema>) => {
    let formData = { ...data } as z.infer<typeof registerUserSchema> & { customCollegeName?: string };
    
    if (formData.college === "other" && customCollegeName.trim()) {
      formData.customCollegeName = customCollegeName.trim();
    }
    
    registerMutation.mutate(formData, {
      onError: (error) => {
        if (error.message.includes("already exists")) {
          form.setError("usn", { 
            type: "manual", 
            message: "This USN is already registered. Please login instead." 
          });
        }
      }
    });
  };
  
  return (
    <Card className="border-slate-200 shadow-sm">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <CardContent className="space-y-4 pt-6">
            <FormField
              control={form.control}
              name="usn"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">University Seat Number</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="e.g., 1SI20CS045 or 22EC101" 
                      {...field}
                      onChange={handleUsnChange}
                      disabled={registerMutation.isPending}
                      className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </FormControl>
                  <FormDescription className="flex flex-col gap-1">
                    {usnError && (
                      <span className="text-red-600 text-sm">
                        {usnError}
                      </span>
                    )}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">Email Address</FormLabel>
                  <FormControl>
                    <Input 
                      type="email"
                      placeholder="your.email@university.edu" 
                      {...field} 
                      disabled={registerMutation.isPending}
                      className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="department"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-700 font-medium">Department</FormLabel>
                    <Select
                      disabled={true}
                      onValueChange={field.onChange}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger className="border-slate-300">
                          <SelectValue placeholder={usnCode ? "Auto-detected" : "Enter USN first"} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {DEPARTMENTS.map((dept) => (
                          <SelectItem key={dept.value} value={dept.value}>
                            {dept.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="year"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-700 font-medium">Year</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(parseInt(value))}
                      value={field.value ? field.value.toString() : undefined}
                      disabled={registerMutation.isPending}
                    >
                      <FormControl>
                        <SelectTrigger className="border-slate-300">
                          <SelectValue placeholder="Select year" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {VALID_YEARS.map((year) => (
                          <SelectItem key={year} value={year.toString()}>
                            Year {year}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <FormField
              control={form.control}
              name="college"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">Institution</FormLabel>
                  {COLLEGE_CODES[collegeCode] ? (
                    <Select
                      disabled={true}
                      onValueChange={field.onChange}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger className="border-slate-300">
                          <SelectValue placeholder="Auto-detected" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {KARNATAKA_COLLEGES.map((college) => (
                          <SelectItem key={college.value} value={college.value}>
                            {college.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : collegeCode || field.value === "other" ? (
                    <div className="flex items-center gap-2">
                      <FormControl>
                        <Input
                          placeholder="Enter your institution name"
                          value={customCollegeName}
                          onChange={(e) => {
                            setCustomCollegeName(e.target.value);
                            field.onChange("other");
                          }}
                          disabled={registerMutation.isPending}
                          className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                        />
                      </FormControl>
                      <input type="hidden" {...field} value="other" />
                    </div>
                  ) : (
                    <Select
                      disabled={true}
                      onValueChange={field.onChange}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger className="border-slate-300">
                          <SelectValue placeholder="Enter USN first" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {KARNATAKA_COLLEGES.map((college) => (
                          <SelectItem key={college.value} value={college.value}>
                            {college.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">Password</FormLabel>
                  <FormControl>
                    <Input 
                      type="password" 
                      placeholder="Create a strong password" 
                      {...field} 
                      disabled={registerMutation.isPending}
                      className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-700 font-medium">Confirm Password</FormLabel>
                  <FormControl>
                    <Input 
                      type="password" 
                      placeholder="Re-enter your password" 
                      {...field} 
                      disabled={registerMutation.isPending}
                      className="border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {registerMutation.error && (
              <div className="text-red-600 text-sm p-3 border border-red-200 rounded-lg bg-red-50">
                {registerMutation.error.message.includes("already exists") 
                  ? "This USN is already registered. Please login instead."
                  : registerMutation.error.message
                }
              </div>
            )}
          </CardContent>
          
          <CardFooter className="flex flex-col gap-3">
            <Button 
              type="submit" 
              className="w-full bg-slate-900 hover:bg-slate-800 text-white" 
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : null}
              Create Account
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}

function ForgotPasswordDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [resetSent, setResetSent] = useState(false);
  const [resetLink, setResetLink] = useState<string | null>(null);
  const { toast } = useToast();
  
  const form = useForm<z.infer<typeof forgotPasswordSchema>>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    }
  });
  
  const onSubmit = async (data: z.infer<typeof forgotPasswordSchema>) => {
    setIsLoading(true);
    
    try {
      const response = await apiRequest('POST', '/api/forgot-password', data);
      const responseData = await response.json();
      if (responseData.resetLink) {
        setResetLink(responseData.resetLink);
      }
      
      setResetSent(true);
      toast({
        title: "Reset email sent",
        description: "If an account exists with that email, you'll receive a password reset link.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send password reset email. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="link" 
          size="sm" 
          className="w-full text-slate-600 hover:text-slate-900"
        >
          Forgot your password?
        </Button>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Reset Password</DialogTitle>
          <DialogDescription>
            {resetSent 
              ? "Check your email for the password reset link."
              : "Enter your email to receive a password reset link."}
          </DialogDescription>
        </DialogHeader>
        
        {resetSent ? (
          <div className="space-y-4">
            {resetLink && (
              <div className="p-3 bg-slate-50 rounded-lg text-sm overflow-auto border border-slate-200">
                <p className="font-semibold mb-2">Demo Only: Password Reset Link</p>
                <p className="break-all text-slate-600">{resetLink}</p>
              </div>
            )}
            <p className="text-sm text-slate-600">
              In a real application, this link would be sent to your email.
            </p>
            <DialogFooter>
              <Button onClick={() => setIsOpen(false)} className="bg-slate-900 hover:bg-slate-800">Close</Button>
            </DialogFooter>
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="your.email@university.edu" 
                        {...field} 
                        disabled={isLoading}
                        className="border-slate-300"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <DialogFooter>
                <Button type="submit" disabled={isLoading} className="bg-slate-900 hover:bg-slate-800">
                  {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Mail className="mr-2 h-4 w-4" />
                  )}
                  Send Reset Link
                </Button>
              </DialogFooter>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  );
}

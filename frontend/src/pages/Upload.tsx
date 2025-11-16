import { usePageVisits } from "@/hooks/use-page-visits";
import { Upload as UploadIcon, Shield, Zap, CheckCircle } from "lucide-react";
import UploadForm from "@/components/notes/UploadForm";

export default function Upload() {
  usePageVisits('upload');
  
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8 sm:py-12">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12">
          <div className="w-12 h-12 sm:w-16 sm:h-16 bg-slate-900 rounded-lg flex items-center justify-center mx-auto mb-4 sm:mb-6">
            <UploadIcon className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
          </div>
          
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4 text-slate-900 px-4">
            Contribute Content
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-slate-600 max-w-2xl mx-auto px-4">
            Share your academic resources with validated, secure uploads
          </p>
        </div>

        {/* Features Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6 mb-8 sm:mb-12 max-w-4xl mx-auto">
          {[
            { icon: Shield, title: "Secure Upload", description: "Enterprise-grade encryption and validation" },
            { icon: Zap, title: "Instant Processing", description: "Automated validation and immediate availability" },
            { icon: CheckCircle, title: "Quality Assured", description: "Automated review and compliance checks" }
          ].map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-lg p-4 sm:p-6 shadow-sm border border-slate-200 text-center hover:shadow-md transition-shadow"
            >
              <div className="w-10 h-10 sm:w-14 sm:h-14 bg-slate-900 rounded-lg flex items-center justify-center mx-auto mb-3 sm:mb-4">
                <feature.icon className="h-5 w-5 sm:h-7 sm:w-7 text-white" />
              </div>
              <h3 className="font-bold text-base sm:text-lg mb-1 sm:mb-2 text-slate-900">{feature.title}</h3>
              <p className="text-xs sm:text-sm text-slate-600">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Upload Form */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 md:p-8 border border-slate-200">
            <UploadForm />
          </div>
        </div>

        {/* Guidelines */}
        <div className="max-w-3xl mx-auto mt-8 sm:mt-12">
          <div className="bg-slate-100 rounded-lg p-4 sm:p-6 border border-slate-200">
            <h3 className="font-bold text-base sm:text-lg mb-3 text-slate-900">📋 Upload Guidelines</h3>
            <ul className="space-y-2 text-sm sm:text-base text-slate-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2 font-bold flex-shrink-0">•</span>
                <span>Ensure content is original or properly attributed</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2 font-bold flex-shrink-0">•</span>
                <span>Use descriptive, professional titles for easy discovery</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2 font-bold flex-shrink-0">•</span>
                <span>Supported formats: PDF, DOC, DOCX, PPT, PPTX, TXT (max 10MB)</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2 font-bold flex-shrink-0">•</span>
                <span>All uploads undergo automated validation and security scanning</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

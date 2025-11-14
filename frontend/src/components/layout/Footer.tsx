import { Building2, BookOpen, Mail, Upload, Home, Search } from "lucide-react";
import { Link } from "wouter";
import { DatabaseStatusIndicator } from "../DatabaseStatus";

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-white py-12 border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <span className="font-bold text-2xl text-white">NotesHub</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              A platform for students to share educational resources, collaborate, and access high-quality notes from peers.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-lg text-white">Quick Links</h3>
            <ul className="space-y-3 text-slate-400">
              <li>
                <Link href="/">
                  <div className="flex items-center text-sm hover:text-blue-400 transition-colors cursor-pointer">
                    <Home className="h-4 w-4 mr-2" />
                    <span>Home</span>
                  </div>
                </Link>
              </li>
              <li>
                <Link href="/find">
                  <div className="flex items-center text-sm hover:text-blue-400 transition-colors cursor-pointer">
                    <Search className="h-4 w-4 mr-2" />
                    <span>Find Notes</span>
                  </div>
                </Link>
              </li>
              <li>
                <Link href="/upload">
                  <div className="flex items-center text-sm hover:text-blue-400 transition-colors cursor-pointer">
                    <Upload className="h-4 w-4 mr-2" />
                    <span>Upload Notes</span>
                  </div>
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-lg text-white">Contact</h3>
            <div className="space-y-3">
              <a 
                href="mailto:tortoor8@gmail.com" 
                className="flex items-center text-sm text-slate-400 hover:text-blue-400 transition-colors"
              >
                <Mail className="h-4 w-4 mr-2" />
                <span>tortoor8@gmail.com</span>
              </a>
            </div>
          </div>
        </div>
        
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center text-sm text-slate-400">
          <div>
            &copy; {new Date().getFullYear()} NotesHub. All rights reserved.
          </div>
          <div className="mt-3 md:mt-0 flex items-center space-x-2">
            <span className="text-xs text-slate-500">System Status:</span>
            <DatabaseStatusIndicator />
          </div>
        </div>
      </div>
    </footer>
  );
}

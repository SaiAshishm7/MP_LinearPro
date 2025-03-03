import { Link } from 'react-router-dom';
import { Mail, Github, Twitter } from 'lucide-react';
import { cn } from "@/lib/utils";

const Footer = ({ className }: { className?: string }) => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className={cn("bg-muted/50 pt-16 pb-8 px-6", className)}>
      <div className="max-w-7xl mx-auto">
        <div className="border-t border-border pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-muted-foreground text-sm mb-4 md:mb-0">
            &copy; {currentYear} Sai Ashish, Lokesh and DR.Sudarshan Babu. All rights reserved.
          </p>
          <div className="flex space-x-6">
            <a 
              href="https://github.com/SaiAshishm7/MP_LinearPro" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors text-sm flex items-center gap-1"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

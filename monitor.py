#!/usr/bin/env python3
"""
Real-Time Monitoring Dashboard for Goalie Scouting Platform
Provides live progress updates as the platform runs
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
import subprocess
import threading
import os

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class RealtimeMonitor:
    """Monitor the goalie scouting platform in real-time"""
    
    def __init__(self):
        self.data_file = Path("goalies_data.json")
        self.blog_dir = Path("blog_posts")
        self.social_file = Path("social_media_tracking.json")
        
        self.start_time = time.time()
        self.stats = {
            "goalies_processed": 0,
            "ai_reports_generated": 0,
            "blog_posts_created": 0,
            "social_posts_created": 0,
            "new_goalies_discovered": 0,
            "errors": 0
        }
        
        self.initial_goalie_count = 0
        if self.data_file.exists():
            with open(self.data_file) as f:
                self.initial_goalie_count = len(json.load(f))
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print dashboard header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.ENDC}  {Colors.BOLD}🏒 BLACK OPS GOALIE SCOUTING PLATFORM - LIVE MONITOR{Colors.ENDC}  {Colors.BOLD}{Colors.CYAN}║{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    def print_stats(self):
        """Print current statistics"""
        elapsed = time.time() - self.start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        
        print(f"{Colors.BOLD}📊 REAL-TIME STATISTICS{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
        
        # Time elapsed
        print(f"⏱️  {Colors.BOLD}Time Elapsed:{Colors.ENDC} {elapsed_str}")
        
        # Goalies stats
        current_count = self.get_current_goalie_count()
        new_count = current_count - self.initial_goalie_count
        print(f"\n{Colors.GREEN}✅ Goalies in Database:{Colors.ENDC} {current_count}")
        if new_count > 0:
            print(f"{Colors.GREEN}🆕 New Goalies Discovered:{Colors.ENDC} {new_count}")
        
        # Processing stats
        print(f"{Colors.BLUE}🤖 AI Reports Generated:{Colors.ENDC} {self.stats['ai_reports_generated']}")
        print(f"{Colors.YELLOW}📝 Blog Posts Created:{Colors.ENDC} {self.stats['blog_posts_created']}")
        print(f"{Colors.CYAN}📱 Social Posts Queued:{Colors.ENDC} {self.stats['social_posts_created']}")
        
        # Errors
        if self.stats['errors'] > 0:
            print(f"{Colors.RED}⚠️  Errors:{Colors.ENDC} {self.stats['errors']}")
        
        # Processing speed
        if elapsed > 0:
            rate = current_count / (elapsed / 60)  # goalies per minute
            print(f"\n{Colors.BOLD}📈 Processing Rate:{Colors.ENDC} {rate:.2f} goalies/minute")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    def get_current_goalie_count(self):
        """Get current number of goalies in database"""
        try:
            if self.data_file.exists():
                with open(self.data_file) as f:
                    return len(json.load(f))
        except:
            pass
        return self.initial_goalie_count
    
    def get_blog_post_count(self):
        """Get number of blog posts created"""
        if self.blog_dir.exists():
            return len(list(self.blog_dir.glob("*.md")))
        return 0
    
    def get_social_post_count(self):
        """Get number of social media posts queued"""
        try:
            if self.social_file.exists():
                with open(self.social_file) as f:
                    data = json.load(f)
                    return len(data.get("posts", []))
        except:
            pass
        return 0
    
    def print_recent_activity(self):
        """Print recent activity log"""
        print(f"{Colors.BOLD}📋 RECENT ACTIVITY{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
        
        # Show last 5 goalies added
        if self.data_file.exists():
            try:
                with open(self.data_file) as f:
                    goalies = json.load(f)
                    recent = sorted(goalies, 
                                  key=lambda x: x.get('discovery_date', ''), 
                                  reverse=True)[:5]
                    
                    for g in recent:
                        name = g.get('name', 'Unknown')
                        league = g.get('league', 'Unknown')
                        tier = g.get('tier', 'Unknown')
                        score = g.get('ai_score', 0)
                        
                        tier_color = Colors.GREEN if tier == "Top Prospect" else Colors.YELLOW
                        print(f"  {tier_color}▸{Colors.ENDC} {name} ({league}) - {tier} - Score: {score}")
            except:
                print(f"  {Colors.YELLOW}Waiting for data...{Colors.ENDC}")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    def print_configuration(self):
        """Print current configuration"""
        print(f"{Colors.BOLD}⚙️  CONFIGURATION{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
        
        # Read .env file
        env_config = {}
        if Path(".env").exists():
            with open(".env") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        env_config[key] = val
        
        ai_provider = env_config.get("AI_PROVIDER", "Not set")
        print(f"  🤖 AI Provider: {Colors.BOLD}{ai_provider}{Colors.ENDC}")
        
        blogging = env_config.get("ENABLE_BLOGGING", "false")
        blog_status = f"{Colors.GREEN}✓ Enabled{Colors.ENDC}" if blogging == "true" else f"{Colors.RED}✗ Disabled{Colors.ENDC}"
        print(f"  📝 Blogging: {blog_status}")
        
        social = env_config.get("ENABLE_SOCIAL", "false")
        dry_run = env_config.get("SOCIAL_DRY_RUN", "true")
        if social == "true":
            if dry_run == "true":
                social_status = f"{Colors.YELLOW}⚠ Dry-Run Mode{Colors.ENDC}"
            else:
                social_status = f"{Colors.GREEN}✓ Live Posting{Colors.ENDC}"
        else:
            social_status = f"{Colors.RED}✗ Disabled{Colors.ENDC}"
        print(f"  📱 Social Media: {social_status}")
        
        maxpreps = env_config.get("ENABLE_MAXPREPS", "false")
        mp_status = f"{Colors.GREEN}✓ Enabled{Colors.ENDC}" if maxpreps == "true" else f"{Colors.RED}✗ Disabled{Colors.ENDC}"
        print(f"  🏫 MaxPreps HS: {mp_status}")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    def update_display(self):
        """Update the dashboard display"""
        self.clear_screen()
        self.print_header()
        self.print_configuration()
        self.print_stats()
        self.print_recent_activity()
        
        print(f"{Colors.BOLD}💡 TIP:{Colors.ENDC} Press Ctrl+C to stop monitoring\n")
    
    def monitor_file_changes(self):
        """Monitor for file changes and update stats"""
        last_goalie_count = self.initial_goalie_count
        last_blog_count = 0
        last_social_count = 0
        
        while True:
            try:
                # Check for changes
                current_goalie_count = self.get_current_goalie_count()
                current_blog_count = self.get_blog_post_count()
                current_social_count = self.get_social_post_count()
                
                # Update stats if changed
                if current_goalie_count > last_goalie_count:
                    self.stats['new_goalies_discovered'] = current_goalie_count - self.initial_goalie_count
                    self.stats['ai_reports_generated'] = current_goalie_count - self.initial_goalie_count
                    last_goalie_count = current_goalie_count
                
                if current_blog_count > last_blog_count:
                    self.stats['blog_posts_created'] = current_blog_count
                    last_blog_count = current_blog_count
                
                if current_social_count > last_social_count:
                    self.stats['social_posts_created'] = current_social_count
                    last_social_count = current_social_count
                
                # Update display
                self.update_display()
                
                # Wait before next check
                time.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.stats['errors'] += 1
                time.sleep(2)
    
    def run_scouting_platform(self):
        """Run the main scouting platform in background"""
        try:
            print(f"\n{Colors.YELLOW}🚀 Starting Black Ops Goalie Scouting Platform...{Colors.ENDC}\n")
            time.sleep(2)
            
            # Run goalie_scout.py in background
            process = subprocess.Popen(
                [sys.executable, "goalie_scout.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return process
            
        except Exception as e:
            print(f"{Colors.RED}Error starting platform: {e}{Colors.ENDC}")
            return None
    
    def run(self):
        """Main monitoring loop"""
        print(f"{Colors.BOLD}{Colors.GREEN}")
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║                                                           ║")
        print("║   🏒 BLACK OPS GOALIE SCOUTING PLATFORM                   ║")
        print("║      Real-Time Monitoring Dashboard                       ║")
        print("║                                                           ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
        
        print(f"{Colors.CYAN}Starting platform and initializing monitoring...{Colors.ENDC}")
        
        # Start the scouting platform
        process = self.run_scouting_platform()
        
        if process:
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_file_changes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            try:
                # Wait for process to complete
                process.wait()
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}⚠️  Monitoring stopped by user{Colors.ENDC}")
                process.terminate()
            
            # Final stats
            print(f"\n{Colors.GREEN}✅ Platform run complete!{Colors.ENDC}")
            self.update_display()
        else:
            # Just monitor without running platform
            print(f"{Colors.YELLOW}Running in monitor-only mode...{Colors.ENDC}\n")
            try:
                self.monitor_file_changes()
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}⚠️  Monitoring stopped{Colors.ENDC}")


if __name__ == "__main__":
    monitor = RealtimeMonitor()
    monitor.run()

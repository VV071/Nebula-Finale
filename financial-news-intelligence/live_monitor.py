"""
Live News Monitor - Real-time terminal display
Connects to the WebSocket stream and displays new articles as they arrive.
"""
import asyncio
import websockets
import json
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for Windows color support
init()


async def monitor_live_news():
    """Connect to live news stream and display updates."""
    
    uri = "ws://127.0.0.1:8000/api/live/stream"
    
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  📡 LIVE NEWS MONITOR - Financial Intelligence Engine{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"{Fore.GREEN}✅ Connected to live stream{Style.RESET_ALL}")
                
                article_count = 0
                
                while True:
                    try:
                        # Receive message
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        msg_type = data.get("type")
                        
                        if msg_type == "connected":
                            print(f"{Fore.BLUE}ℹ️  {data.get('message')}{Style.RESET_ALL}")
                            interval = data.get('interval_minutes')
                            print(f"   Fetch interval: {interval} minute(s)")
                            print(f"   Total processed: {data.get('total_processed')}\n")
                            print(f"{Fore.YELLOW}⏳ Waiting for new articles (updates every {interval} min)...{Style.RESET_ALL}\n")
                            
                            # Send ping to keep alive
                            await websocket.send("ping")
                        
                        elif msg_type == "new_article":
                            article_count += 1
                            article = data.get("article", {})
                            
                            print(f"{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}📰 NEW ARTICLE #{article_count}{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}")
                            
                            headline = article.get("headline", "No headline")
                            print(f"{Fore.WHITE}{Style.BRIGHT}{headline}{Style.RESET_ALL}")
                            
                            print(f"\n{Fore.YELLOW}Source:{Style.RESET_ALL} {article.get('source', 'Unknown')}")
                            print(f"{Fore.YELLOW}Type:{Style.RESET_ALL} {article.get('news_type', 'Unknown')} | "
                                  f"{Fore.YELLOW}Scope:{Style.RESET_ALL} {article.get('scope', 'Unknown')}")
                            
                            impact = article.get("impact", {})
                            direction = impact.get("direction", "Unknown")
                            confidence = impact.get("confidence", 0)
                            
                            # Color code impact
                            if direction == "Positive":
                                impact_color = Fore.GREEN
                            elif direction == "Negative":
                                impact_color = Fore.RED
                            else:
                                impact_color = Fore.YELLOW
                            
                            print(f"{Fore.YELLOW}Impact:{Style.RESET_ALL} {impact_color}{direction}{Style.RESET_ALL} "
                                  f"(confidence: {confidence:.2f}) | "
                                  f"Horizon: {impact.get('time_horizon', 'Unknown')}")
                            
                            print(f"{Fore.YELLOW}Published:{Style.RESET_ALL} {article.get('published_at', 'Unknown')}")
                            print()
                            
                            # Send ping to keep alive
                            await websocket.send("ping")
                        
                        elif msg_type == "stats_update":
                            stats = data.get("stats", {})
                            print(f"\n{Fore.BLUE}📊 Stats Update:{Style.RESET_ALL}")
                            print(f"   Last fetch: {stats.get('last_fetch', 'Never')}")
                            print(f"   New articles: {stats.get('new_articles', 0)}")
                            print(f"   Total processed: {stats.get('total_processed', 0)}\n")
                            
                            # Send ping to keep alive
                            await websocket.send("ping")
                    
                    except websockets.exceptions.ConnectionClosed:
                        print(f"\n{Fore.RED}❌ Connection closed by server{Style.RESET_ALL}")
                        break
                    except json.JSONDecodeError:
                        continue
                    except KeyboardInterrupt:
                        raise
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Disconnecting...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔄 Retrying in 5 seconds...{Style.RESET_ALL}")
            await asyncio.sleep(5)



if __name__ == "__main__":
    try:
        asyncio.run(monitor_live_news())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}✅ Monitor stopped{Style.RESET_ALL}")

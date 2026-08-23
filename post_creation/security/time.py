import time
from datetime import datetime, timezone

print("Server time:", datetime.now(timezone.utc))
print("Server timestamp:", time.time())
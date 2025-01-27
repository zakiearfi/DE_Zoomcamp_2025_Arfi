{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Connection failed for db:5432: could not translate host name \"db\" to address: No such host is known. \n",
      "\n",
      "Connection failed for postgres:5432: could not translate host name \"postgres\" to address: No such host is known. \n",
      "\n"
     ]
    }
   ],
   "source": [
    "import psycopg2\n",
    "\n",
    "# Two possible connection configurations based on Docker Compose\n",
    "connection_configs = [\n",
    "    {\n",
    "        'host': 'db',     # Service name\n",
    "        'port': 5432,     # Internal container port\n",
    "        'database': 'ny_taxi',\n",
    "        'user': 'postgres',\n",
    "        'password': 'postgres'\n",
    "    },\n",
    "    {\n",
    "        'host': 'postgres',  # Container name\n",
    "        'port': 5432,        # Internal container port\n",
    "        'database': 'ny_taxi',\n",
    "        'user': 'postgres',\n",
    "        'password': 'postgres'\n",
    "    }\n",
    "]\n",
    "\n",
    "def test_connection(config):\n",
    "    try:\n",
    "        conn = psycopg2.connect(**config)\n",
    "        print(f\"Successfully connected using {config['host']}:{config['port']}\")\n",
    "        conn.close()\n",
    "        return True\n",
    "    except Exception as e:\n",
    "        print(f\"Connection failed for {config['host']}:{config['port']}: {e}\")\n",
    "        return False\n",
    "\n",
    "# Test both connection configurations\n",
    "for config in connection_configs:\n",
    "    test_connection(config)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

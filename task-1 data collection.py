{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyMbbEXaBNfku1KP6QOKq9nJ",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Samiksha2-cloud/Trendpulse-samiksha-yadav/blob/main/task-1%20data%20collection.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import os\n",
        "import json\n",
        "import requests\n",
        "import time\n",
        "from datetime import datetime\n",
        "\n",
        "# --- 1. Configuration & Constants ---\n",
        "BASE_URL = \"https://hacker-news.firebaseio.com/v0\"\n",
        "HEADERS = {\"User-Agent\": \"TrendPulse/1.0\"}\n",
        "DATA_FOLDER = \"data\"\n",
        "STORY_LIMIT_PER_CATEGORY = 25\n",
        "TOTAL_STORIES_TO_SCAN = 500\n",
        "\n",
        "# Fixed: Added commas and ensured proper dictionary structure\n",
        "CAT = {\n",
        "    \"technology\": [\"AI\", \"software\", \"tech\", \"code\", \"computer\", \"data\", \"cloud\", \"API\", \"GPU\", \"LLM\"],\n",
        "    \"worldnews\": [\"war\", \"government\", \"country\", \"president\", \"election\", \"climate\", \"attack\", \"global\"],\n",
        "    \"sports\": [\"NFL\", \"NBA\", \"FIFA\", \"sport\", \"game\", \"team\", \"player\", \"league\", \"championship\"],\n",
        "    \"science\": [\"science\", \"research\", \"study\", \"space\", \"physics\", \"biology\", \"discovery\", \"NASA\", \"genome\"],\n",
        "    \"entertainment\": [\"movie\", \"film\", \"music\", \"Netflix\", \"game\", \"book\", \"show\", \"award\", \"streaming\"]\n",
        "}\n",
        "\n",
        "def get_category(title):\n",
        "    \"\"\"Assigns a category based on keywords found in the title (case-insensitive).\"\"\"\n",
        "    title_lower = title.lower()\n",
        "    for category, keywords in CAT.items():\n",
        "        for keyword in keywords:\n",
        "            if keyword.lower() in title_lower:\n",
        "                return category\n",
        "    return None\n",
        "\n",
        "def fetch_data():\n",
        "    \"\"\"Main execution function to fetch, process, and save story data.\"\"\"\n",
        "\n",
        "    # Create the directory if it doesn't exist\n",
        "    if not os.path.exists(DATA_FOLDER):\n",
        "        os.makedirs(DATA_FOLDER)\n",
        "        print(f\"Created directory: {DATA_FOLDER}\")\n",
        "\n",
        "    # 2. Fetch the top story IDs\n",
        "    try:\n",
        "        print(\"Fetching top story IDs...\")\n",
        "        response = requests.get(f\"{BASE_URL}/topstories.json\", headers=HEADERS)\n",
        "        response.raise_for_status()\n",
        "        story_ids = response.json()[:TOTAL_STORIES_TO_SCAN]\n",
        "    except Exception as e:\n",
        "        print(f\"Failed to fetch top stories: {e}\")\n",
        "        return\n",
        "\n",
        "    collected_data = []\n",
        "    # Tracking counts to respect the 25-per-category limit\n",
        "    counts = {cat: 0 for cat in CAT.keys()}\n",
        "\n",
        "    print(\"Processing stories... this may take a moment.\")\n",
        "\n",
        "    # 3. Fetch individual story details\n",
        "    for story_id in story_ids:\n",
        "        # Stop if we have filled all categories (Optimization)\n",
        "        if all(count >= STORY_LIMIT_PER_CATEGORY for count in counts.values()):\n",
        "            print(\"Reached the limit for all categories.\")\n",
        "            break\n",
        "\n",
        "        try:\n",
        "            item_url = f\"{BASE_URL}/item/{story_id}.json\"\n",
        "            item_res = requests.get(item_url, headers=HEADERS)\n",
        "            item_res.raise_for_status()\n",
        "            story = item_res.json()\n",
        "\n",
        "            # Skip if it's not a story or has no title\n",
        "            if not story or 'title' not in story:\n",
        "                continue\n",
        "\n",
        "            category = get_category(story['title'])\n",
        "\n",
        "            # If it matches a category and we still need more for that category\n",
        "            if category and counts[category] < STORY_LIMIT_PER_CATEGORY:\n",
        "                story_entry = {\n",
        "                    \"post_id\": story.get(\"id\"),\n",
        "                    \"title\": story.get(\"title\"),\n",
        "                    \"category\": category,\n",
        "                    \"score\": story.get(\"score\", 0),\n",
        "                    \"num_comments\": story.get(\"descendants\", 0),\n",
        "                    \"author\": story.get(\"by\"),\n",
        "                    \"collected_at\": datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n",
        "                }\n",
        "\n",
        "                collected_data.append(story_entry)\n",
        "                counts[category] += 1\n",
        "\n",
        "                # Check if we JUST hit the limit for this specific category\n",
        "                if counts[category] == STORY_LIMIT_PER_CATEGORY:\n",
        "                    print(f\"Finished collecting for: {category}. Cooling down for 2 seconds...\")\n",
        "                    time.sleep(2)\n",
        "\n",
        "        except Exception as e:\n",
        "            print(f\"Error fetching item {story_id}: {e}\")\n",
        "            continue\n",
        "\n",
        "    # 4. Save to JSON file\n",
        "    date_str = datetime.now().strftime(\"%Y%m%d\")\n",
        "    filename = f\"{DATA_FOLDER}/trends_{date_str}.json\"\n",
        "\n",
        "    with open(filename, \"w\") as f:\n",
        "        json.dump(collected_data, f, indent=4)\n",
        "\n",
        "    print(f\"--- SUCCESS ---\")\n",
        "    print(f\"Collected {len(collected_data)} stories total.\")\n",
        "    print(f\"Saved to {filename}\")\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    fetch_data()"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "eUlYADXpxlVj",
        "outputId": "91f152d1-31e3-426b-85a1-6a30d7ee2f10"
      },
      "execution_count": 24,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Fetching top story IDs...\n",
            "Processing stories... this may take a moment.\n",
            "Finished collecting for: technology. Cooling down for 2 seconds...\n",
            "Finished collecting for: entertainment. Cooling down for 2 seconds...\n",
            "--- SUCCESS ---\n",
            "Collected 78 stories total.\n",
            "Saved to data/trends_20260405.json\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "hQ765WAE2PZn"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
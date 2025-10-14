{
  "title": "Lights Summary",
  "config": {
    "step": {
      "user": {
        "title": "Create Lights Summary Sensor",
        "description": "Select an area and a label to create a summary sensor that shows how many lights or switches are on in that area.",
        "data": {
          "area_name": "Area",
          "label_name": "Device label"
        }
      }
    },
    "error": {
      "no_areas": "No areas found in your Home Assistant configuration."
    },
    "abort": {
      "no_areas": "No areas are defined. Please add an area first in Home Assistant."
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Configure Lights Summary",
        "description": "Adjust the area or label if needed.",
        "data": {
          "area_name": "Area",
          "label_name": "Device label"
        }
      }
    }
  }
}


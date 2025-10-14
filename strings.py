{
  "title": "Lights Summary",
  "config": {
    "step": {
      "user": {
        "title": "Select Area",
        "description": "Choose the area where you want to create a Lights Summary sensor.",
        "data": {
          "area_name": "Area",
          "label_name": "Device label"
        }
      }
    },
    "abort": {
      "no_areas": "No areas are defined. Please add an area first.",
      "already_configured": "A Lights Summary sensor for this area and label already exists.",
      "invalid_area": "The selected area is invalid or has been deleted."
    },
    "error": {
      "already_configured": "A Lights Summary sensor with this area and label already exists."
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Edit Lights Summary",
        "description": "Change the area or label for this sensor.",
        "data": {
          "area_name": "Area",
          "label_name": "Device label"
        }
      }
    }
  }
}

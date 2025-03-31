# Run this script to fix your JSON format
library(jsonlite)
library(dplyr)

# Function to fix JSON structure
fix_travel_details_json <- function() {
  # Try different possible file paths
  possible_paths <- c(
    "referee_travel_details.json",
    "~/Desktop/workfiles/referee_travel_details.json"
  )
  
  file_path <- NULL
  for(path in possible_paths) {
    if(file.exists(path)) {
      file_path <- path
      break
    }
  }
  
  if(is.null(file_path)) {
    stop("Could not find referee_travel_details.json file!")
  }
  
  # Load the current JSON data
  tryCatch({
    details <- fromJSON(file_path)
    
    # Check if it's already in the right format
    if(is.list(details) && !is.data.frame(details)) {
      cat("JSON file appears to be in the correct format.\n")
      return(details)
    }
    
    # Convert to the correct format if needed
    formatted_details <- list()
    
    if(is.data.frame(details)) {
      # Convert from data frame to list of referees
      for(i in 1:nrow(details)) {
        ref <- details[i,]
        ref_name <- ref$referee
        
        # Extract travel legs if they exist
        legs <- list()
        if("travel_legs" %in% names(ref) && !is.null(ref$travel_legs)) {
          if(is.character(ref$travel_legs)) {
            # If legs are stored as JSON string, parse them
            legs <- fromJSON(ref$travel_legs)
          } else {
            legs <- ref$travel_legs
          }
        }
        
        formatted_details[[i]] <- list(
          referee = ref_name,
          games_officiated = ref$games_officiated,
          total_travel_miles = ref$total_travel_miles,
          travel_legs = legs
        )
      }
    }
    
    # Write the fixed JSON
    fixed_path <- paste0(tools::file_path_sans_ext(file_path), "_fixed.json")
    write_json(formatted_details, fixed_path, auto_unbox = TRUE, pretty = TRUE)
    cat("Fixed JSON saved to:", fixed_path, "\n")
    
    # Return the fixed data
    return(formatted_details)
    
  }, error = function(e) {
    cat("Error processing JSON file:", e$message, "\n")
    stop("Failed to process the JSON file.")
  })
}

# Run the function
fixed_details <- fix_travel_details_json() 
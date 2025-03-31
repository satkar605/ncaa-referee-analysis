# NCAA Referee Analysis with Leaflet Map
# install.packages(c("shiny", "tidyverse", "DT", "leaflet", "jsonlite"))

library(shiny)
library(tidyverse)
library(DT)
library(leaflet)
library(jsonlite)

# Define the null coalescing operator
`%||%` <- function(x, y) if(is.null(x)) y else x

# Define UI with map tab
ui <- fluidPage(
  # App title
  titlePanel("NCAA Basketball Referee Analysis"),
  
  # Sidebar layout
  sidebarLayout(
    sidebarPanel(
      # Input: Select referee for map
      selectInput("map_referee", "Select Referee for Travel Map:",
                  choices = c("Loading...")),
      
      # Input: Select variable for ranking
      radioButtons("sort_var", "Rank Referees By:",
                  choices = c("Total Travel Miles" = "Total_Travel_Miles",
                             "Games Officiated" = "Games_Officiated",
                             "Unique Venues" = "Unique_Venues"),
                  selected = "Total_Travel_Miles"),
      
      # Filter by minimum games
      sliderInput("min_games", "Minimum Games Officiated:",
                  min = 1, max = 30, value = 5),
      
      # Help text
      helpText("This app analyzes NCAA basketball referee travel patterns."),
      helpText("Make sure your data files are in the same folder as app.R")
    ),
    
    # Main panel with results
    mainPanel(
      tabsetPanel(
        tabPanel("Referee Rankings", 
                 h3("Top Referees"),
                 DT::dataTableOutput("ref_table")),
        
        tabPanel("Summary Statistics", 
                 h3("Key Metrics"),
                 verbatimTextOutput("summary_stats"),
                 plotOutput("histogram")),
        
        tabPanel("Travel Map",
                 h3("Referee Travel Routes"),
                 leafletOutput("travel_map", height = "500px"),
                 verbatimTextOutput("map_stats")),
        
        tabPanel("Debug Info", 
                 h3("Data File Information"),
                 verbatimTextOutput("debug_info")),
                 
        tabPanel("Test Map", 
                 h3("Test Leaflet Map"),
                 leafletOutput("test_map", height = "500px"))
      )
    )
  )
)

# Define server logic
server <- function(input, output, session) {
  
  # Debug info to check files
  output$debug_info <- renderPrint({
    # Check if files exist
    cat("Checking data files:\n")
    cat("referee_travel.csv exists:", file.exists("referee_travel.csv"), "\n")
    cat("referee_travel_details.json exists:", file.exists("referee_travel_details.json"), "\n")
    cat("referee_travel_details_fixed.json exists:", file.exists("referee_travel_details_fixed.json"), "\n")
    cat("venue_coordinates.csv exists:", file.exists("venue_coordinates.csv"), "\n")
    cat("venue_cache.json exists:", file.exists("venue_cache.json"), "\n")
    
    # If files exist, check their content
    if(file.exists("referee_travel.csv")) {
      refs <- read_csv("referee_travel.csv")
      cat("\nNumber of referees in CSV:", nrow(refs), "\n")
      cat("First few referees:", paste(head(refs$Referee), collapse=", "), "\n")
    }
    
    # Try both original and fixed JSON files
    json_path <- NULL
    if(file.exists("referee_travel_details_fixed.json")) {
      json_path <- "referee_travel_details_fixed.json"
    } else if(file.exists("referee_travel_details.json")) {
      json_path <- "referee_travel_details.json"
    }
    
    if(!is.null(json_path)) {
      tryCatch({
        details <- fromJSON(json_path)
        cat("\nJSON file format:", class(details)[1], "\n")
        cat("Number of referees in details:", length(details), "\n")
        
        if(length(details) > 0) {
          if(is.list(details) && !is.data.frame(details)) {
            cat("First referee in details:", details[[1]]$referee, "\n")
            cat("Number of legs for first referee:", length(details[[1]]$travel_legs), "\n")
          } else if(is.data.frame(details)) {
            cat("First referee in details:", details$referee[1], "\n")
            cat("Travel legs column exists:", "travel_legs" %in% names(details), "\n")
          }
        }
      }, error = function(e) {
        cat("Error reading JSON file:", e$message, "\n")
      })
    }
    
    # Check venue data
    if(file.exists("venue_cache.json")) {
      tryCatch({
        venue_cache <- fromJSON("venue_cache.json")
        cat("\nVenue cache format:", class(venue_cache)[1], "\n")
        cat("Number of venues in cache:", length(venue_cache), "\n")
        
        # Create venue coordinates if needed
        if(!file.exists("venue_coordinates.csv")) {
          cat("\nCreating venue_coordinates.csv from venue_cache.json...\n")
          venue_df <- data.frame(
            venue = names(venue_cache),
            latitude = sapply(venue_cache, function(x) x[1]),
            longitude = sapply(venue_cache, function(x) x[2]),
            stringsAsFactors = FALSE
          )
          write.csv(venue_df, "venue_coordinates.csv", row.names = FALSE)
          cat("Created venue_coordinates.csv with", nrow(venue_df), "venues\n")
        }
      }, error = function(e) {
        cat("Error reading venue cache:", e$message, "\n")
      })
    }
  })
  
  # Basic test map
  output$test_map <- renderLeaflet({
    leaflet() %>%
      addProviderTiles(providers$CartoDB.Positron) %>%
      addMarkers(lng = -95, lat = 39, popup = "Test Marker") %>%
      setView(lng = -95, lat = 39, zoom = 4)
  })
  
  # Read referee data
  ref_data <- reactive({
    tryCatch({
      read_csv("referee_travel.csv")
    }, error = function(e) {
      cat("Error reading referee_travel.csv:", e$message, "\n")
      tibble(
        Referee = character(),
        Games_Officiated = numeric(),
        Total_Travel_Miles = numeric(),
        Unique_Venues = numeric()
      )
    })
  })
  
  # Read travel details data - try both original and fixed JSON
  travel_details <- reactive({
    # Try fixed JSON first, then original
    if(file.exists("referee_travel_details_fixed.json")) {
      tryCatch({
        details <- fromJSON("referee_travel_details_fixed.json")
        return(details)
      }, error = function(e) {
        cat("Error reading fixed JSON:", e$message, "\n")
      })
    }
    
    # Try original JSON
    if(file.exists("referee_travel_details.json")) {
      tryCatch({
        details <- fromJSON("referee_travel_details.json")
        
        # Convert data frame to list if needed
        if(is.data.frame(details)) {
          formatted_details <- list()
          for(i in 1:nrow(details)) {
            ref <- details[i,]
            formatted_details[[i]] <- list(
              referee = ref$referee,
              games_officiated = ref$Games_Officiated,
              total_travel_miles = ref$Total_Travel_Miles,
              travel_legs = list() # Empty list since we don't have legs
            )
          }
          return(formatted_details)
        }
        
        return(details)
      }, error = function(e) {
        cat("Error reading JSON:", e$message, "\n")
        return(list())
      })
    } else {
      return(list())
    }
  })
  
  # Read venue coordinates
  venue_coords <- reactive({
    # First try venue_coordinates.csv
    if(file.exists("venue_coordinates.csv")) {
      return(read_csv("venue_coordinates.csv"))
    }
    
    # If not found, try to create from venue_cache.json
    if(file.exists("venue_cache.json")) {
      tryCatch({
        venue_cache <- fromJSON("venue_cache.json")
        
        venue_df <- data.frame(
          venue = names(venue_cache),
          latitude = sapply(venue_cache, function(x) x[1]),
          longitude = sapply(venue_cache, function(x) x[2]),
          stringsAsFactors = FALSE
        )
        
        # Save for future use
        write.csv(venue_df, "venue_coordinates.csv", row.names = FALSE)
        
        return(venue_df)
      }, error = function(e) {
        cat("Error creating venue coordinates:", e$message, "\n")
        return(tibble(venue = character(), latitude = numeric(), longitude = numeric()))
      })
    } else {
      return(tibble(venue = character(), latitude = numeric(), longitude = numeric()))
    }
  })
  
  # Update referee dropdown based on available data
  observe({
    req(ref_data())
    ref_choices <- ref_data()$Referee
    updateSelectInput(session, "map_referee", 
                     choices = c("Select a referee" = "", ref_choices))
  })
  
  # Filter data based on inputs
  filtered_data <- reactive({
    req(ref_data())
    ref_data() %>%
      filter(Games_Officiated >= input$min_games) %>%
      arrange(desc(.data[[input$sort_var]]))
  })
  
  # Get travel details for selected referee
  selected_referee_details <- reactive({
    req(input$map_referee, travel_details())
    
    # Debug logging
    cat("Looking for referee:", input$map_referee, "\n")
    cat("Number of referees in travel_details:", length(travel_details()), "\n")
    
    # Find the selected referee in the travel details
    ref_details <- NULL
    
    # Only proceed if we have travel details
    if(length(travel_details()) > 0) {
      # Get all referee names from the details
      all_refs <- sapply(travel_details(), function(x) {
        if(is.null(x$referee)) return("Unknown")
        return(x$referee)
      })
      
      cat("First few referees in details:", paste(head(all_refs), collapse=", "), "\n")
      
      # Find the index of the selected referee
      ref_idx <- which(all_refs == input$map_referee)
      cat("Match found at index:", paste(ref_idx, collapse=", "), "\n")
      
      # Get the details if found
      if(length(ref_idx) > 0) {
        ref_details <- travel_details()[[ref_idx[1]]]
        cat("Found details for referee:", ref_details$referee, "\n")
        cat("Travel legs available:", !is.null(ref_details$travel_legs), "\n")
        cat("Number of legs:", length(ref_details$travel_legs), "\n")
      }
    }
    
    return(ref_details)
  })
  
  # Create the travel map for selected referee
  output$travel_map <- renderLeaflet({
    req(input$map_referee != "", venue_coords())
    
    # Get referee details
    ref_details <- selected_referee_details()
    
    # Create base map
    m <- leaflet() %>%
      addProviderTiles(providers$CartoDB.Positron)
    
    # If we don't have travel details or legs, return empty map
    if(is.null(ref_details) || is.null(ref_details$travel_legs) || length(ref_details$travel_legs) == 0) {
      return(m %>% 
               setView(-95, 39, zoom = 4) %>%
               addControl("No travel data available for this referee", position = "topright"))
    }
    
    # Get venue coordinates
    venues <- venue_coords()
    
    # Create a list to store venue visits
    venue_visits <- list()
    
    # Process travel legs
    for(leg in ref_details$travel_legs) {
      from_venue <- leg$from_venue
      to_venue <- leg$to_venue
      
      # Skip if venues are missing
      if(is.null(from_venue) || is.null(to_venue)) next
      
      # Get coordinates for from venue
      from_coords <- venues %>% 
        filter(venue == from_venue)
      
      # Get coordinates for to venue
      to_coords <- venues %>% 
        filter(venue == to_venue)
      
      # Only add route if we have coordinates for both venues
      if(nrow(from_coords) > 0 && nrow(to_coords) > 0) {
        # Add route
        m <- m %>%
          addPolylines(
            lng = c(from_coords$longitude[1], to_coords$longitude[1]),
            lat = c(from_coords$latitude[1], to_coords$latitude[1]),
            color = "blue",
            weight = 2,
            opacity = 0.8,
            popup = paste(
              "<strong>Date:</strong>", leg$date, "<br>",
              "<strong>From:</strong>", from_venue, "<br>",
              "<strong>To:</strong>", to_venue, "<br>",
              "<strong>Distance:</strong>", round(leg$distance, 1), "miles"
            )
          )
        
        # Track venues for markers
        venue_visits[[from_venue]] <- (venue_visits[[from_venue]] %||% 0) + 1
        venue_visits[[to_venue]] <- (venue_visits[[to_venue]] %||% 0) + 1
      }
    }
    
    # Add venue markers
    for(venue_name in names(venue_visits)) {
      venue_row <- venues %>% filter(venue == venue_name)
      if(nrow(venue_row) > 0) {
        count <- venue_visits[[venue_name]]
        m <- m %>%
          addCircleMarkers(
            lng = venue_row$longitude[1],
            lat = venue_row$latitude[1],
            radius = 4 + (count * 2),  # Size based on visits
            color = "red",
            fillOpacity = 0.7,
            popup = paste(
              "<strong>Venue:</strong>", venue_name, "<br>",
              "<strong>Visits:</strong>", count
            )
          )
      }
    }
    
    # Return the map
    m
  })
  
  # Display map statistics
  output$map_stats <- renderPrint({
    req(input$map_referee)
    
    # Get referee details
    ref_details <- selected_referee_details()
    
    if(is.null(ref_details)) {
      return("No travel data available for this referee.")
    }
    
    # Calculate statistics
    total_games <- ref_details$games_officiated
    total_miles <- ref_details$total_travel_miles
    
    cat("Travel Statistics for:", ref_details$referee, "\n")
    cat("-------------------------------------\n")
    cat("Total Games Officiated:", total_games, "\n")
    cat("Total Travel Miles:", round(total_miles, 0), "\n")
    
    # Calculate leg statistics if available
    if(!is.null(ref_details$travel_legs) && length(ref_details$travel_legs) > 0) {
      leg_distances <- sapply(ref_details$travel_legs, function(x) {
        if(is.null(x$distance)) return(NA)
        return(x$distance)
      })
      leg_distances <- leg_distances[!is.na(leg_distances)]
      
      if(length(leg_distances) > 0) {
        cat("Number of Travel Legs:", length(leg_distances), "\n")
        cat("Average Miles per Trip:", round(mean(leg_distances), 0), "\n")
        cat("Longest Trip:", round(max(leg_distances), 0), "miles\n")
      } else {
        cat("Travel leg details not available.\n")
      }
    } else {
      cat("No travel legs data available for this referee.\n")
    }
  })
  
  # Output: Referee Rankings Table
  output$ref_table <- DT::renderDataTable({
    filtered_data() %>%
      select(Referee, Games_Officiated, Total_Travel_Miles, Unique_Venues) %>%
      mutate(Total_Travel_Miles = round(Total_Travel_Miles, 0)) %>%
      rename(
        "Referee Name" = Referee,
        "Games" = Games_Officiated,
        "Travel Miles" = Total_Travel_Miles,
        "Venues" = Unique_Venues
      )
  })
  
  # Output: Summary Statistics
  output$summary_stats <- renderPrint({
    if(nrow(filtered_data()) == 0) {
      return("No data available. Please check that your referee_travel.csv file is in the app directory.")
    }
    
    cat("REFEREE TRAVEL ANALYSIS\n")
    cat("------------------------\n")
    cat("Total Referees:", nrow(filtered_data()), "\n")
    cat("Average Travel Miles:", round(mean(filtered_data()$Total_Travel_Miles), 0), "\n")
    cat("Average Games Officiated:", round(mean(filtered_data()$Games_Officiated), 1), "\n")
    cat("Most Active Referee:", filtered_data() %>% 
          arrange(desc(Games_Officiated)) %>% 
          slice(1) %>% 
          pull(Referee), "\n")
    cat("Referee with Most Travel:", filtered_data() %>% 
          arrange(desc(Total_Travel_Miles)) %>% 
          slice(1) %>% 
          pull(Referee), "\n")
  })
  
  # Output: Histogram of the selected variable
  output$histogram <- renderPlot({
    if(nrow(filtered_data()) == 0) {
      return(NULL)
    }
    
    # Create labels map
    labels <- c(
      "Total_Travel_Miles" = "Travel Miles",
      "Games_Officiated" = "Games Officiated",
      "Unique_Venues" = "Unique Venues"
    )
    
    # Create histogram
    ggplot(filtered_data(), aes_string(x = input$sort_var)) +
      geom_histogram(fill = "steelblue", color = "white", bins = 15) +
      labs(
        title = paste("Distribution of", labels[input$sort_var]),
        x = labels[input$sort_var],
        y = "Number of Referees"
      ) +
      theme_minimal()
  })
}

# Run the application
shinyApp(ui = ui, server = server) 
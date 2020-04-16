library(readxl)
library(plyr)
library(readr)
library(purrr)
library(stringr)
library(fuzzyjoin)

#covid <- read.csv("covid data.csv", sep = "")
#state_pops <- read_excel("nst-est2019-01.xlsx", skip = 8 )

#pops <- state_pops[,c(1,13)]
#colnames(pops) <- c("state", "pop")

#states <- read.csv("state_names_and_abbrevs.csv", header = FALSE)

setwd("state_district_links/")

myfiles = list.files(path=getwd(), pattern="*.csv", full.names=TRUE)
dat_csv = ldply(myfiles, read.csv, header = FALSE)

# grab pct missing
myfunc <- function(file){
  df <- read.csv(file, header = FALSE)
  sum(is.na(df$V2)) / length(df$V2)
}

myfiles = list.files(path=getwd(), pattern="*.csv", full.names=TRUE)

# grab n missing
myfunc2 <- myfunc <- function(file){
  df <- read.csv(file, header = FALSE)
  sum(is.na(df$V2)) 
}

# grab n total
myfunc3 <- function(file){
  df <- read.csv(file, header = FALSE)
  length(df$V2)
}

pct_miss <- data.frame(
  states$V1,
  unlist(map(myfiles, myfunc)),
  unlist(map(myfiles, myfunc2)),
  unlist(map(myfiles, myfunc3))
)


colnames(pct_miss) <- c("State", "PCT Missing URL", "N missing", "N total")

pct_miss$`PCT Links Found` <- 1 - pct_miss$`PCT Missing URL`
pct_miss$`N found` <- pct_miss$`N total` - pct_miss$`N missing`

write.csv(pct_miss, "missing_pcts_new.csv")

# read in nces data
nces_data <- read.csv("~/Downloads/district-data.csv")

nces_data$state <- tolower(nces_data$state)

# alabama test case
alabama <- dplyr::filter(nces_data, state == "alabama")

alabama$district.name <- tolower(alabama$district.name)

Alabama2 <- read.csv("Alabama.csv", header = FALSE)

colnames(Alabama2) <- c("district.name", "website.url")

Alabama2$V1 <- tolower(str_trim(str_replace(Alabama2$V1, "School District", "")))

commons <- Alabama2$district.name[Alabama2$district.name %in% alabama$district.name]

Alabama2[Alabama2$district.name %in% alabama$district.name,]

overlap <- alabama[alabama$district.name %in% commons,]

nourl <- overlap[is.na(overlap$website.url),]$district.name

test <- merge(Alabama2, alabama, by = "district.name", all.x = TRUE, all.y = TRUE)

# grab all the state files from greatschools
myfiles = list.files(path="states_data", pattern="*.csv", full.names=TRUE)
#dat_csv = ldply(myfiles, read.csv, header = FALSE)

# get rid of DC  and split on state
nces_data <- nces_data[nces_data$state != "district of columbia",]
nces_split <- split(nces_data, nces_data$state)

# create list of merged data frames
df_list <- list()

# merge the data frames
for (i in 1:50){
  grschools <- read.csv(myfiles[i], header = FALSE)
  colnames(grschools) <- c("district.name", "website.url")
  
  grschools$district.name <- tolower(str_trim(str_replace(grschools$district.name, "School District", "")))
  
  nces <- nces_split[[i]]
  nces$district.name <- tolower(nces$district.name)
  
  merged <- merge(grschools, nces, by = "district.name", all.x = TRUE, all.y = TRUE)
  
  colnames(merged)[c(2,5)] <- c("Great Schools URL", "NCES URL")
  #assign(names(nces_split[i]), merged)
  df_list[[length(df_list) + 1]] <- merged
  
}





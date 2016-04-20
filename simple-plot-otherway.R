p <- "/Users/austinstig/Developer/CS512/src/january.txt";
data <- read.csv(p, header=TRUE, sep = ",");
# get day of week
data$day <-weekdays(as.Date(strptime(data$time, "%Y-%m-%d %H:%M:%S")));
data$hour <-as.numeric(strftime(strptime(data$time, "%Y-%m-%d %H:%M:%S"), "%H"));
# segment by education type
edu <- subset(data, edu == 1);
non_edu <- subset(data, edu == 0);

# segment by hour
b <- c()
colors <- c()
for (hr in seq(1,23)) {
  # subset data
  e <- subset(edu, hour = hr);
  n <- subset(non_edu, hour = hr);
  # append data
  b<- append(b, sum(e$score)/sum(e$count));
  b<- append(b, sum(n$score)/sum(n$count));
  # append color
  colors<-append(colors, "blue");
  colors<-append(colors, "red");
}

# plot bars
barplot(b, col=colors);



# segment by hour
b <- c()
colors <- c()
for (dy in c("Monday", "Tuesday","Wednesday","Thursday","Friday")) {
  # subset data
  e <- subset(edu, day == dy);
  n <- subset(non_edu, day == dy);
  # append data
  b<- append(b, sum(e$score)/sum(e$count));
  b<- append(b, sum(n$score)/sum(n$count));
  # append color
  colors<-append(colors, "blue");
  colors<-append(colors, "red");
}

# plot bars
#barplot(b, col=colors);

# apply moving averages
#mover <- function(x, win=5) { filter(x, rep(1/win, win), sides=2) }
#plot(edu$window, mover(edu$score), col="blue", type="l");
#lines(edu$window, mover(not_edu$score), col="red");


  
  

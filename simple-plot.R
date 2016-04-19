library(sqldf)
p <- "/Users/austinstig/Developer/CS512/src/january.txt";
data <- read.csv(p, header = TRUE, sep = ",");
edu <- subset(data, edu == 1);
non_edu <- subset(data, edu == 0);

lines(edu$window, edu$score, col="blue");
lines(edu$window, not_edu$score, col="red");

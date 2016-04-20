p <- "/Users/austinstig/Developer/CS512/src/january.txt";
data <- read.csv(p, header=TRUE, sep = ",");
# get day of week
data$day <-weekdays(as.Date(strptime(data$time, "%Y-%m-%d %H:%M:%S")));
# segment by education type
edu <- subset(data, edu == 1);
non_edu <- subset(data, edu == 0);

# segment by weekday
em <- subset(edu, day == "Monday");
et <- subset(edu, day == "Tuesday");
ew <- subset(edu, day == "Wednesday");
er <- subset(edu, day == "Thursday");
ef <- subset(edu, day == "Friday");
nm <- subset(non_edu, day == "Monday");
nt <- subset(non_edu, day == "Tuesday");
nw <- subset(non_edu, day == "Wednesday");
nr <- subset(non_edu, day == "Thursday");
nf <- subset(non_edu, day == "Friday");

b <- c(mean(em$score * em$count/max(em$count)), mean(nm$score* nm$count/max(nm$count)),
       mean(et$score * et$count/max(et$count)), mean(nt$score* nt$count/max(nt$count)),
       mean(ew$score * ew$count/max(ew$count)), mean(nw$score* nw$count/max(nw$count)),
       mean(er$score * er$count/max(er$count)), mean(nr$score* nr$count/max(nr$count)),
       mean(ef$score * ef$count/max(ef$count)), mean(nf$score* nf$count/max(nf$count))
);
colors <- c("blue", "red",
            "blue", "red",
            "blue", "red",
            "blue", "red",
            "blue", "red"
);
barplot(b, col=colors)

# apply moving averages
#mover <- function(x, win=5) { filter(x, rep(1/win, win), sides=2) }
#plot(edu$window, mover(edu$score), col="blue", type="l");
#lines(edu$window, mover(not_edu$score), col="red");


  
  

d = read.csv("out/evaluation.csv")
d$batch = factor(paste(d$note, "-", d$batch))

d$found = d$found - d$incorrect
d$incorrect = NULL

# The baseline grade, 6.0, will be given if your algorithm terminates in less than 30 minutes, producing at
# least 10 valid pairs of similar users. Moreover, you can get up to 1.0 extra point for:
# • the average number of found pairs per minute,
# • the total number of found pairs (over 5 different runs),
# • the median run time (over 5 different runs),
# • code readability, elegance.


tbl = data.frame()
for (batch in levels(d$batch)) {
  b = d[d$batch == batch, ]
  
  tbl = rbind(tbl, data.frame(
    batch = batch,
    
    ppm = mean(b$ppm),
    ppm.sd = sd(b$ppm),
  
    found = mean(b$found),
    found.sd = sd(b$found),
    
    median_time = median(b$time / 60)
  ))
}

print(tbl)

t23 = tbl[grepl("23", tbl$batch), ]
t24 = tbl[grepl("24", tbl$batch), ]

library(ggplot2)
require(gridExtra)


d = read.csv("out/ec_experiments.csv", header = T)
d$sig_len = d$bands * d$rows

d$batch = ifelse(as.character(d$run_id) < "2017-10-22T00:42", 1, 
                 ifelse(as.character(d$run_id) < "2017-10-22T01:33", 2, 3))
d$signature_alg = factor(ifelse(d$batch %in% c(1), "permutations", "min-hashing"))

d = d[d$batch >= 3, ]
d$batch = factor(d$batch)

end = d[seq(nrow(d), 1, -1), ]
end = end[!duplicated(end$run_id), ]
end$ppm = end$count / (end$time / 60)


d = merge(d, end[, c("run_id", "ppm")], by = "run_id", all.x = T)


p1 = ggplot(d, aes(x = time, y = count,
                   group = run_id,
                   color = ppm)) +
  geom_line(aes(linetype = batch))

p2 = ggplot(end, aes(x = bands, y = rows,
                     size = count,
                     fill = count)) +
  geom_point(aes(color = batch), shape = 21, alpha = .8)

grid.arrange(p1, p2, ncol = 2)


print(end[order(-end$count)[1:5], c("batch", "bands", "rows", "sig_len", "max_buckets", "count")])
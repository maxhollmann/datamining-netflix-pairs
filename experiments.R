library(ggplot2)
require(gridExtra)


d = read.csv("out/ec_experiments.csv", header = T)
d$sig_len = d$bands * d$rows

d$run_id = factor(as.character(d$run_id))
d$params = factor(paste(d$bands, d$rows))

d = d[order(d$batch_id, d$run_id, d$time), ]

d = d[d$batch_id == "2017-10-22T22:48:42.248160", ]

end = d[seq(nrow(d), 1, -1), ]
end = end[!duplicated(end$run_id), ]
end$ppm = end$count / (end$time / 60)


d = merge(d, end[, c("run_id", "ppm")], by = "run_id", all.x = T)
d = d[d$time > 1, ]

p1 = ggplot(d, aes(x = time, y = count,
                   group = run_id,
                   color = ppm)) +
  geom_line(aes(linetype = factor(bands))) +
  scale_x_continuous(name = "Minutes after start",
                     breaks = seq(0, 1800, 120), labels = seq(0, 30, 2),
                     limits = c(NA, NA))

# p2 = ggplot(end, aes(x = bands, y = rows,
#                      size = count,
#                      fill = ppm)) +
#   geom_point(color = "black", shape = 21, alpha = .6, position = position_jitter(0.14, 0.14)) +
#   scale_size(range = c(0.2, 20)) +
#   scale_fill_continuous(low = 'blue', high = 'red')


end$fail_rate = 0
for (b in unique(d$bands)) {
  end[end$bands == b, ]$fail_rate = mean(end[end$bands == b, ]$count < 150)
}
p2 = ggplot(end, aes(x = bands, y = count,
                     size = ppm,
                     fill = fail_rate)) +
  geom_point(color = "black", shape = 21, alpha = .3, position = position_jitter(0.24, 0.24)) +
  scale_size(range = c(0.2, 20)) +
  scale_fill_continuous(low = 'green', high = 'red') +
  scale_x_continuous(name = "Bands",
                     breaks = sort(unique(end$bands)))

grid.arrange(p1, p2, ncol = 2)


end = end[end$fail_rate < 0.05, ]
print(end[order(end$count), c("run_id", "batch_id", "bands", "rows", "sig_len", "max_buckets", "fail_rate", "count", "ppm")])

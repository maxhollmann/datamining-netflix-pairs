library(ggplot2)
require(gridExtra)

d = read.csv("out/ec_experiments.csv", header = T)
d$sig_len = d$bands * d$rows


end = d[seq(nrow(d), 1, -1), ]
end = end[!duplicated(end$run_id), ]
end$ppm = end$count / (end$time / 60)


d = merge(d, end[, c("run_id", "ppm")], by = "run_id", all.x = T)


p1 = ggplot(d, aes(x = time, y = count,
                   group = run_id,
                   color = ppm)) +
  geom_line()

p2 = ggplot(end, aes(x = bands, y = rows,
                     size = sig_len,
                     fill = count)) +
  geom_point(shape = 21, alpha = .8)

grid.arrange(p1, p2, ncol = 2)

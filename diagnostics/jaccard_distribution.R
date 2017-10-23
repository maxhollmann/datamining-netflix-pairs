d = read.csv("out/jaccard_dist.csv", header = T)
d = d[!duplicated(d[, c("u1", "u2")]), ]
d = d[1:7000, ]


djaccard = function(sim, p = opt$estimate) {
  dbeta(sim, p[1], p[2])
}

loglik = function(p) {
  -sum(log(djaccard(d$jac_sim, p)))
}
opt = nlm(loglik, c(1.5, 2))


print(opt$estimate)

hist(d$jac_sim, breaks = 27, freq = F)
lines(density(d$jac_sim), col = 'green')

s = seq(0, 1, .001)
lines(s, djaccard(s, opt$estimate), col = 'red')

legend(0.25, 6, legend = c("Data", "Fitted distribution"), lwd = 1, col = c('green', 'red'))


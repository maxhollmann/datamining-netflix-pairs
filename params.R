source("jaccard_distribution.R")


sensitivity = function(true_sim, rows, bands) {
  1 - (1 - true_sim^rows) ^ bands
}

true_sim = seq(0, 1, .001)
sens = sensitivity(true_sim, rows=7, bands=15)
baseline = djaccard(true_sim)

par(mfrow = c(1, 2))
plot(true_sim, sens, type = 'l')
lines(true_sim, baseline)

plot(true_sim, baseline*sens, type = 'l')


abline(v = .5)

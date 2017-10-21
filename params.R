p = function(s, rows, bands) {
  #r = siglen/bands
  1 - (1 - s^rows) ^ bands
}

s = seq(0, 1, .001)
sensitivity = p(s, rows=40, bands=3)
dist = dbeta(xs, a, b)

par(mfrow = c(1, 2))
plot(s, sensitivity, type = 'l')
lines(xs, dist)

plot(s, dist*sensitivity, type = 'l')


abline(v = .5)

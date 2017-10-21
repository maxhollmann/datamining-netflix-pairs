d = read.csv("out/all.csv", header = T)
d = d[!duplicated(d[, c("u1", "u2")]), ]

print(nrow(d))


fit = lm(jac_sim ~ sig_sim + I(sig_sim^2), d)
print(summary(fit))

pred_sig = seq(0, 1, .01)
pred_jac = predict(fit, newdata = data.frame(sig_sim = pred_sig))

plot(jac_sim ~ sig_sim, d, type = 'p')
abline(0, 1, col = "green", lwd = 2)
lines(pred_sig, pred_jac, col = "red", lwd = 2)


print(paste("Found", sum(d$jac_sim >= .5), "/", nrow(d), "with true similarity >= .5"))


# dd = data.frame()
# for (i in 1:nrow(d)) {
#   r = d[i, ]
#   rows = d[rep(i, r$n), ]
#   dd = rbind(dd, rows)
# }

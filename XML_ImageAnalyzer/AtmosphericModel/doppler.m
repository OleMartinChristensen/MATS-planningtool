function fi = doppler(AD, niu_niu0)
fi = sqrt(log(2)/pi)/AD * exp(-log(2)*niu_niu0.^2 / AD^2);
end

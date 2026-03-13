function Debug(...)
    if GetConvarInt(GetCurrentResourceName() .. "_debug", 0) ~= 0 or GetConvarInt("lemon_debug", 0) ~= 0 then
        print(...)
    end
end
